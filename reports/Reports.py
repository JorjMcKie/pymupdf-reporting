import io

import fitz

HEADER_RECT = None


class FrontMatterReport(object):
    def __init__(self, mediabox, margins=None, logo=None):
        self.mediabox = mediabox
        if margins == None:
            self.where = self.mediabox + (36, 36, -36, -50)
        else:
            L, T, R, B = margins
            self.where = self.mediabox + (L, T, -R, -B)
        if isinstance(logo, str):
            self.logo_file = logo
            self.logo_rect = fitz.Rect(
                self.where.tl, self.where.x0 + 100, self.where.y0 + 100
            )
        else:
            self.logo_file = None
        self.page0 = []
        self.pages = []

    def run(self, filename):
        details = None
        for sect in self.page0 + self.pages:
            if not isinstance(sect, fitz.Story):
                sect.make_story()
            if hasattr(sect, "header_tops"):
                details = sect
        fp = io.BytesIO()
        pno = 0
        writer = fitz.DocumentWriter(fp)
        more = True
        while more:
            more_list = []
            if pno == 0:
                sections = self.page0
            else:
                sections = self.pages
            dev = writer.begin_page(self.mediabox)
            where = +self.where
            for sect in sections:
                if sect == details:
                    if pno > 0:
                        where.y0 += sect.HEADER_RECT.height

                    sect.header_tops.append(where.y0)
                    this_more, filled = sect.story.place(where)
                    where.y0 = filled[3]
                    sect.story.draw(dev)
                    more_list.append(this_more)
                else:
                    sect.story.reset()
                    this_more, filled = sect.story.place(where)
                    where.y0 = filled[3]
                    sect.story.draw(dev)
                    more_list.append(this_more)
            writer.end_page()
            pno += 1
            more = any(more_list)
        writer.close()

        doc = fitz.open("pdf", fp)
        page_count = doc.page_count

        for page in doc:
            page.wrap_contents()
            page.insert_image(self.logo_rect, filename=self.logo_file)
            btm_rect = fitz.Rect(
                self.where.x0, self.where.y1 + 15, self.where.x1, page.rect.y1
            )
            page.insert_textbox(
                btm_rect,
                f"Page {page.number+1} of {page_count}",
                align=fitz.TEXT_ALIGN_CENTER,
            )
            if details == None:
                continue
            if page.number > 0:
                rect = +details.HEADER_RECT
                rect.y1 = details.header_tops[page.number]
                rect.y0 = rect.y1 - details.HEADER_RECT.height
                details.repeat_header(page, rect)
            elif isinstance(details.top_row_bg, str):
                fill = details.top_row_bg
                if fill[0] == "#":
                    fill = fill[1:]
                try:
                    fill = int(fill, base=16)
                    fill = fitz.sRGB_to_pdf(fill)
                    details.top_row_bg = fill
                except ValueError:
                    fill = details.top_row_bg = (1, 1, 1)
                delta = details.HEADER_RECT.y0 - self.where.y0
                rect = +details.HEADER_RECT
                rect.y0 = details.header_tops[0] + delta
                rect.y1 = rect.y0 + details.HEADER_RECT.height
                page.draw_rect(rect, color=None, fill=fill, overlay=False)

        doc.ez_save(filename)


class SimpleBlock(object):
    def __init__(self, html=None, archive=None, css=None, story=None):
        self.html = html
        self.archive = archive if archive else "."
        self.css = css
        self.story = story

    def make_story(self):
        if not isinstance(self.story, fitz.Story):
            self.story = fitz.Story(self.html, user_css=self.css, archive=self.archive)


class LongTable(object):
    def __init__(
        self,
        report,
        html=None,
        story=None,
        columns=[],
        fetch_rows=None,
        top_row=None,
        top_row_bg=None,
        archive=None,
        css=None,
    ):
        self.mediabox = report.mediabox
        self.where = report.where
        self.html = html
        self.story = story
        self.top_row = top_row
        self.top_row_bg = top_row_bg
        self.story = None
        self.column_ids = columns
        self.archive = "." if not archive else archive
        self.css = css
        self.fetch_rows = fetch_rows
        self.HEADER_RECT = None
        self.HEADER_BLOCKS = None
        self.HEADER_PATHS = None
        self.header_tops = []

    def extract_header(self):
        global HEADER_RECT

        def recorder(pos):
            global HEADER_RECT
            if pos.open_close != 2:
                return
            if pos.id != pos.header:
                return
            HEADER_RECT = fitz.Rect(pos.rect)

        fp = io.BytesIO()
        writer = fitz.DocumentWriter(fp)
        dev = writer.begin_page(self.mediabox)
        _, _ = self.story.place(self.where)
        self.story.element_positions(recorder, {"page": 0, "header": self.top_row})
        self.story.draw(dev)
        writer.end_page()
        writer.close()
        doc = fitz.open("pdf", fp)
        page = doc[0]
        paths = [p for p in page.get_drawings() if p["rect"].intersects(HEADER_RECT)]
        blocks = page.get_text("dict", clip=HEADER_RECT)["blocks"]
        doc.close()
        bbox = fitz.EMPTY_RECT()
        for p in paths:
            bbox |= p["rect"]
        for b in blocks:
            bbox |= b["bbox"]
        self.story.reset()
        self.HEADER_RECT = +HEADER_RECT
        HEADER_RECT = None
        self.HEADER_BLOCKS = blocks
        self.HEADER_PATHS = paths
        return

    def make_story(self):
        if isinstance(self.story, fitz.Story):
            return
        self.story = fitz.Story(self.html, user_css=self.css, archive=self.archive)
        body = self.story.body
        table = body.find("table", None, None)
        if table == None:
            raise ValueError("no table found in the HTML")
        templ = body.find(None, "id", "template")  # locate template row
        if templ == None:
            raise ValueError("cannot find row 'template'")

        rows = self.fetch_rows()
        for data in rows:
            row = templ.clone()  # clone model row
            for i in range(len(data)):
                text = str(data[i]).replace("\\n", "\n").replace("<br>", "\n")
                tag = row.find(None, "id", self.column_ids[i])
                if tag == None:
                    raise ValueError(f"id '{self.comlumn_ids[i]}' not in template row.")
                _ = tag.add_text(text)
            table.append_child(row)
            # print("row appended")

        templ.remove()
        if self.top_row != None:
            self.extract_header()

    def repeat_header(self, page, rect):
        page.draw_rect(rect, color=None, fill=self.top_row_bg, overlay=False)
        mat = self.HEADER_RECT.torect(rect)

        for p in self.HEADER_PATHS:
            for item in p["items"]:
                if item[0] == "l":
                    page.draw_line(item[1] * mat, item[2] * mat, color=p["color"])
                elif item[0] == "re":
                    page.draw_rect(item[1] * mat, color=p["color"], fill=p["fill"])

        for block in self.HEADER_BLOCKS:
            for line in block["lines"]:
                for span in line["spans"]:
                    point = fitz.Point(span["origin"]) * mat
                    if "bold" in span["font"].lower():
                        fontname = "hebo"
                    else:
                        fontname = "helv"
                    page.insert_text(
                        point, span["text"], fontname=fontname, fontsize=span["size"]
                    )

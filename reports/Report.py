import io
import fitz

HEADER_RECT = None
FOOTER_RECT = None

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

class NColumnsReport(object):
    def __init__(self, mediabox, margins=None, logo=None, columns=1, header=None, footer=None):
        self.mediabox = mediabox
        self.margins = margins
        self.columns = columns # column number, 2 as default
        self.sections = [] # sections list
        self.header = header
        self.footer = footer
        self.sindex = 0
        self.COLS = columns
        self.HEADER_RECT = None
        self.FOOTER_RECT = None

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

    def current(self):      
        if isinstance(self.sections[self.sindex], list):
            return self.sections[self.sindex][0]
        return self.sections[self.sindex]
    
    def check_cols(self):
        columns = self.COLS
        if len(self.sections) > self.sindex and isinstance(self.sections[self.sindex], list):
            if not isinstance(self.sections[self.sindex][1], int):
                TypeError("Columns type error")
            
            if len(self.sections[self.sindex]) != 2:
                BufferError("Size is not matched")

            columns = self.sections[self.sindex][1]
        if self.COLS is columns: # still with current COLS
            return False
        else:
            self.COLS = columns # new page
            return True
    
    def run(self, filename):
        # init
        self.sindex = 0

        if not isinstance(self.header, fitz.Story) and self.header is not None:
            self.header.make_story()
            _, self.HEADER_RECT = self.header.story.place(self.where)

            self.where.y0 = self.HEADER_RECT[3]
        
        if not isinstance(self.footer, fitz.Story) and self.footer is not None:
            self.footer.make_story()
            _, self.FOOTER_RECT = self.footer.story.place(self.mediabox)

            footer_height = self.FOOTER_RECT[3]

            self.FOOTER_RECT = tuple([
                                self.FOOTER_RECT[0],
                                self.where.y1 - footer_height,
                                self.FOOTER_RECT[2],
                                self.mediabox.y1
                            ])
            self.where.y1 = self.where.y1 - footer_height # adjust content rect

        for section in self.sections: # create story
            if not isinstance(section, fitz.Story):
                if isinstance(section, list): 
                    section[0].make_story()
                else:
                    section.make_story()

        fileobject = io.BytesIO()  # let DocumentWriter write to memory
        writer = fitz.DocumentWriter(fileobject)  # define output writer

        more = True # need more pages or not
        self.check_cols() # init COLS

        while more:  # loop until all input text has been written out
            dev = writer.begin_page(self.mediabox)  # prepare a new output page

            if self.header is not None: # draw Header
                self.header.story = None # delete
                self.header.make_story()
                self.header.story.place(self.HEADER_RECT)
                self.header.story.draw(dev, None)
            
            ROWS = 1 # default
            TABLE = fitz.make_table(self.where, cols=self.COLS, rows=ROWS) # layouts
            CELLS = [TABLE[i][j] for i in range(ROWS) for j in range(self.COLS)]

            CELL_LENGTH = len(CELLS) # get Length of Cells
            more_cell = True
            cell_index = 0 # columns index
            where = CELLS[cell_index] # temp where
            
            while more_cell: # loop until it reach out max column count in one page
                # content may be complete after any cell, ...
                if more:  # so check this status first
                    more, filled = self.current().story.place(where) # draw current section
                    self.current().story.draw(dev, None)
                print(filled[3], self.where.y1, more)
                if filled[3] < self.where.y1 -2 : # check and add section/block
                    if more == 0:
                        self.sindex += 1
                        if self.check_cols():
                            cell_index = CELL_LENGTH # create new page

                    where.y0 = filled[3] # update latest position for next drawing
                
                if more and filled[3] >= self.where.y1 -2: # check and select next column
                    cell_index += 1
                
                if cell_index is CELL_LENGTH: # check whether one page is completed
                    more_cell = False

                if more_cell: # update next React with completion
                    where = CELLS[cell_index]
                more = True # set to draw

                if self.sindex >= len(self.sections): # check completion of PDF
                    more = False
                    more_cell = False
            
            if self.footer is not None: # draw Footer
                self.footer.story = None
                self.footer.make_story()
                self.footer.story.place(self.FOOTER_RECT)
                self.footer.story.draw(dev, None)

            writer.end_page()  # finish the PDF page
        
        writer.close()

        doc = fitz.open("pdf", fileobject)
        page_count = doc.page_count

        for page in doc: # draw footer with page number
            page.wrap_contents()
            page.insert_image(self.logo_rect, filename=self.logo_file)
            btm_rect = fitz.Rect(
                self.where.x0, self.mediabox.y1 - 30, self.where.x1, page.rect.y1
            )
            page.insert_textbox( # draw page number
                btm_rect,
                f"Page {page.number+1} of {page_count}",
                align=fitz.TEXT_ALIGN_CENTER,
            )

        doc.ez_save(filename) # save

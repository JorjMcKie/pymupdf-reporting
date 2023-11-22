import fitz
import pathlib
import json
from Reports import Report, Table, Block, ImageBlock

report = Report(
    fitz.paper_rect("a4-l"), font_families={"sans-serif": "ubuntu", "serif": "ubuntu"}
)

# Read the report header HTML. To be shown on every page
header_html = pathlib.Path("header.html").read_text()
header = Block(html=header_html, report=report)

# Define the logo
logo = ImageBlock(url="logo.png", height=100, report=report)

# -------------------------------------------------------------------
# Read the "prolog" HTML. Things to be shown on page 1 only.
# -------------------------------------------------------------------
prolog_html = pathlib.Path("prolog.html").read_text()

# The prolog HTML contains 4 variables, which must be replaced by
# real data: "supplier", "contact", "billto" and "shipto".
supplier = json.loads(pathlib.Path("supplier.json").read_text())
prolog_story = fitz.Story(html=prolog_html)
body = prolog_story.body
body.find(None, "id", "supplier").add_text(supplier["supplier"])
body.find(None, "id", "contact").add_text(supplier["contact"])
body.find(None, "id", "billto").add_text(supplier["billto"])
body.find(None, "id", "shipto").add_text(supplier["shipto"])


# Read the detail items HTML. To be shown as a table.
detail_html = pathlib.Path("detail.html").read_text()

# Make a Story object for prolog, header and logo image
prolog = Block(story=prolog_story, report=report)


def fetch_rows():
    """Read invoice items from any database."""
    # Items are in some JSON file for this demo's purposes
    items = json.loads(pathlib.Path("items.json").read_text())

    # defines the field names used in the items HTML
    toprow = ["line", "hp-id", "desc", "part", "qty", "uom", "date", "uprice", "tprice"]
    rows = [toprow]  # must be row 0 when returning

    # We also computate anything required for the report here, e.g. total price
    total_price = 0.0
    for data in items:
        rows.append(
            [
                data["line"],
                data["hp-id"],
                data["desc"],
                data["part"],
                data["qty"],
                data["uom"],
                data["date"],
                data["uprice"],
                data["tprice"],
            ]
        )
        price = float(data["tprice"][1:])  # extract total price
        total_price += price
    last_row = [""] * 7
    rows.append(last_row + ["Total:", f"${round(total_price,2)}"])

    return rows


detail = Table(
    report=report,
    html=detail_html,
    fetch_rows=fetch_rows,
    top_row="toprow",
)

report.header = [logo, header]
report.sections = [prolog, detail]

report.run("invoice.pdf")

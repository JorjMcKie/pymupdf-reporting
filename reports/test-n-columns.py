import pathlib
import fitz
import sqlite3
from Report import SimpleBlock, LongTable, NColumnsReport

# The following defines the overall report object
mediabox = fitz.paper_rect("letter-l")  # the only required parameter
report = NColumnsReport(mediabox, logo="logo.png")

# Predefined HTML to define the header for all pages
springer_html = pathlib.Path("springer.html").read_bytes().decode()
springer = SimpleBlock(html=springer_html, archive=".")

springer_html2 = pathlib.Path("springer.html").read_bytes().decode()
springer2 = SimpleBlock(html=springer_html2, archive=".")

hdr_html = pathlib.Path("header.html").read_bytes().decode()
header = SimpleBlock(html=hdr_html)

footer_html = pathlib.Path("header.html").read_bytes().decode()
footer = SimpleBlock(html=footer_html)

# Predefined HTML for any information only occurring on page 1
prolog_html = pathlib.Path("prolog.html").read_bytes().decode()
prolog = SimpleBlock(html=prolog_html)

springer_html1 = pathlib.Path("springer.html").read_bytes().decode()
springer1 = SimpleBlock(html=springer_html, archive=".")

def fetch_rows():
    """Read invoice items and return them to the report generator.

    This is a callback function called by the report generator.
    """
    database = sqlite3.connect("invoice-parms.db")
    cursor = database.cursor()
    select = (
        'select line, "hp-id", desc, part,qty, uom,date,'
        "uprice, qty*uprice"
        ' from "invoice-items" order by line'
    )
    cursor.execute(select)
    rows = cursor.fetchall()
    row_len = len(rows[0])
    total = 0
    for i in range(len(rows)):
        total += rows[i][-1]  # add to the total prices
    total_row = [""] * row_len
    total_row[-2] = "Total:"
    total_row[-1] = total
    rows.append(total_row)
    return rows

items_html = pathlib.Path("test-header.html").read_bytes().decode()

items = LongTable(  # generate an object spanning pages
    html=items_html,  # HTML source
    fetch_rows=fetch_rows,  # callback delivering invoice items
    columns=[  # 'id' items in the HTML source
        "line",
        "hp-id",
        "desc",
        "part",
        "qty",
        "uom",
        "date",
        "uprice",
        "tprice",
    ],
    top_row="header",  # identifies top table's top row
    top_row_bg="#aaceeb",  # top row background color
    report=report,  # pointer to owning report object
)

report.sections = [springer2, springer, [items, 1], [springer1, 5]]  # set sections list
report.header = header
report.footer = footer

# This generates the report and saves it to the given path name.
report.run("pymupdf-invoice.pdf")

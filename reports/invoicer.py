import pathlib
import sqlite3

import fitz

from Reports import FrontMatterReport, LongTable, SimpleBlock

# The following defines the overall report object
mediabox = fitz.paper_rect("letter-l")  # the only required parameter
report = FrontMatterReport(
    mediabox,
    logo="logo.png",  # put this image at the top-left of all pages
)

# Predefined HTML to define the header for all pages
hdr_html = pathlib.Path("header.html").read_bytes().decode()
header = SimpleBlock(html=hdr_html)

# Prepare the "prolog" for page 1. Following data would normally be
# exctracted from a data base.
supplier = """Artifex Software, Inc.
39 Mesa Street
Suite 108A
San Francisco, CA 94129
UNITED STATES
"""

contact = """Artifex Software, Inc.
39 Mesa Street
Suite 108A
San Francisco, CA 94129
UNITED STATES
"""

shipto = """Paul Atreides (Muad'Dib)
The Emperor's Palace
Arrakeen
Planet Arrakis (Dune)
"""

billto = """Jorj X. McKie, Saboteur Extraordinary
Bureau of Sabotage
Central City
Planet Central-Central
"""

# The prolog HTML basically is a skeleton with 4 variables
prolog_html = pathlib.Path("prolog.html").read_bytes().decode()

# After reading the source, we access the content and fill in
# data for the variables.
prolog_story = fitz.Story(prolog_html)
body = prolog_story.body
body.find(None, "id", "supplier").add_text(supplier)
body.find(None, "id", "contact").add_text(contact)
body.find(None, "id", "billto").add_text(billto)
body.find(None, "id", "shipto").add_text(shipto)

# Now define the building block. Because we have modified the HTML, we
# use the prepared Story instead of the original HTML source.
prolog = SimpleBlock(story=prolog_story)


def fetch_rows():
    """Read and return invoice items.

    This is a callback function called by the report generator.
    In the general case, any type of data could be accessed here,
    like JSON, CSV, or other databases.

    In our example, we are reading an sqlite database und manipulate
    the rows a bit before returning them.
    """
    database = sqlite3.connect("invoice-parms.db")  # contains invoice items
    cursor = database.cursor()  # make a cursor

    # extract invoice items
    select = (
        'select line, "hp-id", desc, part,qty, uom,date,'
        "uprice, qty*uprice"
        ' from "invoice-items" order by line'
    )
    cursor.execute(select)  # read the invoice items into a list
    rows = cursor.fetchall()

    # we need some modifications for the report:
    row_len = len(rows[0])  # number of rows
    total = 0  # total price of the invoice
    for i in range(len(rows)):  # walk through the rows
        row = list(rows[i])  # make sure to have a modifiable list
        uprice, tprice = row[-2:]  # read the prices
        total += tprice  # add to the total prices
        # modify items to show the currency
        row[-1] = f"${tprice}"
        row[-2] = f"${uprice}"
        rows[i] = row  # update the rows list

    # add a final row with the invoice total
    total_row = [""] * row_len
    total_row[-2] = "Total:"
    total_row[-1] = f"${round(total,2)}"

    # append the totals row
    rows.append(total_row)

    # prepend a row with the HTML field id's:
    fields = [  # 'id' items in the HTML source
        "line",
        "hp-id",
        "desc",
        "part",
        "qty",
        "uom",
        "date",
        "uprice",
        "tprice",
    ]
    rows.insert(0, fields)
    return rows


# Read the HTML source code for the items table
items_html = pathlib.Path("items.html").read_bytes().decode()

items = LongTable(  # generate a table object that can cross page boundaries
    html=items_html,  # HTML source
    fetch_rows=fetch_rows,  # callback to fetch invoice items
    top_row="header",  # identifies the table's top row
    top_row_bg="#aaceeb",  # top row background color
    report=report,  # pointer to owning report object
)

# -----------------------------------------------------------------------------
# We have defined all required building blocks for the report.
# Now define on which pages they should be used.
# Report type "FrontMatterReport" supports this by two separate lists
# of building blocks:
# One for the first page and one for all other pages.
# -----------------------------------------------------------------------------

# Attribute 'page0' can contain a different set of stories than other pages
report.page0 = [header, prolog, items]  # page 1 has 3 building blocks
report.pages = [header, items]  # other pages show the header and item details

# This generates the report and saves it to the given path name.
report.run("pymupdf-invoice1.pdf")

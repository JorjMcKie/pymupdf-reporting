import pathlib
import fitz
import sqlite3
import zipfile
from pprint import pprint
from Reports import Block, Table, Report, ImageBlock

# The following defines the overall report object
mediabox = fitz.paper_rect("a4-l")  # the only required parameter
report = Report(mediabox)

# Predefined HTML to define the header for all pages
springer_html = pathlib.Path("n-columns/springer.html").read_bytes().decode()
springer = Block(html=springer_html, archive=".", report=report)

HEADER = """<h2 style="text-align:center;font-family: sans-serif;">Members of the NATO</h2>"""
HTML = """
<style>
body {font-family: sans-serif;font-size: 14px;}
td, th {
    padding-left: 10px;
    padding-right: 10px;
}

.even {background-color: #ccc;} /* use for alternating background */
.odd {background-color: #fff;} /* use for alternating background */

</style>

<body>
<table>
<tr id="header">
    <th>Country</th>
    <th>Type</th>
    <th>Flag</th>
    <th>Since</th>
</tr>

<tr id="template">
    <td id="country"></td>
    <td id="member"></td>
    <td id="flag"></td>
    <td id="since"></td>
</tr>
</table>
</body>
"""

national_flags = zipfile.ZipFile("national-flags.zip")


def fetch_rows():
    table_data = """country;member;flag;since
    Belgium;Founder;|img|Belgium.jpg;1949
    Denmark;Founder;|img|Denmark.jpg;1949
    France;Founder;|img|France.jpg;1949
    Iceland;Founder;|img|Iceland.jpg;1949
Italy;Founder;|img|Italy.jpg;1949
Canada;Founder;|img|Canada.jpg;1949
Luxembourg;Founder;|img|Luxembourg.jpg;1949
Netherlands;Founder;|img|Netherlands.jpg;1949
Norway;Founder;|img|Norway.jpg;1949
Portugal;Founder;|img|Portugal.jpg;1949
United Kingdom;Founder;|img|United_Kingdom.jpg;1949
United States;Founder;|img|United_States.jpg;1949
Greece;Joiner;|img|Greece.jpg;1952
Turkey;Joiner;|img|Turkey.jpg;1952
Germany;Joiner;|img|Germany.jpg;1955
Spain;Joiner;|img|Spain.jpg;1982
Poland;Joiner;|img|Poland.jpg;1999
Czech Republic;Joiner;|img|Czech_Republic.jpg;1999
Hungary;Joiner;|img|Hungary.jpg;1999
Bulgaria;Joiner;|img|Bulgaria.jpg;2004
Estonia;Joiner;|img|Estonia.jpg;2004
Latvia;Joiner;|img|Latvia.jpg;2004
Lithuania;Joiner;|img|Lithuania.jpg;2004
Romania;Joiner;|img|Romania.jpg;2004
Slovakia;Joiner;|img|Slovakia.jpg;2004
Slovenia;Joiner;|img|Slovenia.jpg;2004
Albania;Joiner;|img|Albania.jpg;2009
Croatia;Joiner;|img|Croatia.jpg;2009
Montenegro;Joiner;|img|Montenegro.jpg;2017
North Macedonia;Joiner;|img|North_Macedonia.jpg;2020
Finland;Joiner;|img|Finland.jpg;2023
Sweden;Joiner;|img|Sweden.jpg;2023
"""
    data = [l.split(";") for l in table_data.splitlines()]
    return data

def fetch_rows_items():
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
# items_html = pathlib.Path("items.html").read_bytes().decode()

# items = Table(  # generate a table object that can cross page boundaries
#     html=items_html,  # HTML source
#     fetch_rows=fetch_rows_items,  # callback to fetch invoice items
#     top_row="header",  # identifies the table's top row
#     top_row_bg="#aaceeb",  # top row background color
#     report=report,  # pointer to owning report object
#     alternating_bg=("#ccc", "#aaa", "#fff"),
# )

logo = ImageBlock(url="./logo.png", width=100, height=100, report=report)
header = Block(html=HEADER, report=report)
items = Table(
    report=report,
    html=HTML,
    top_row="header",
    top_row_bg="#aaceeb",
    fetch_rows=fetch_rows,
    archive=national_flags,
    alternating_bg=("#ccc", "#aaa", "#fff"),
)

report.sections = [[springer, 3], [items, 2],]  # set sections list
report.header = [logo, header]
report.footer = [logo, ]

# This generates the report and saves it to the given path name.
report.run("pymupdf-invoice.pdf")
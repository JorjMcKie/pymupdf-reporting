"""
Demo script using (Py-) MuPDF "Story" feature.

"""
import zipfile
from pprint import pprint
from Reports import LongTable, FrontMatterReport, SimpleBlock
import fitz

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


report = FrontMatterReport(fitz.paper_rect("a5"))
header = SimpleBlock(html=HEADER, report=report)
items = LongTable(
    report=report,
    html=HTML,
    top_row="header",
    top_row_bg="#ffff00",
    fetch_rows=fetch_rows,
    archive=national_flags,
    alternating_bg=("#c0c0c0", "#ffffff"),
)

report.pages = report.page0 = [header, items]
report.run("NATO.pdf")

"""
Demo script using (Py-) MuPDF "Story" feature.

"""
import zipfile
from pprint import pprint
from Reports import LongTable, FrontMatterReport
import fitz


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
<h2 style="text-align:center">Members of the NATO</h2>
<table style="margin-left: 20%;">
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
    Belgium;Founder;Belgium.jpg;1949
    Denmark;Founder;Denmark.jpg;1949
    France;Founder;France.jpg;1949
    Iceland;Founder;Iceland.jpg;1949
Italy;Founder;Italy.jpg;1949
Canada;Founder;Canada.jpg;1949
Luxembourg;Founder;Luxembourg.jpg;1949
Netherlands;Founder;Netherlands.jpg;1949
Norway;Founder;Norway.jpg;1949
Portugal;Founder;Portugal.jpg;1949
United Kingdom;Founder;United_Kingdom.jpg;1949
United States;Founder;United_States.jpg;1949
Greece;Joiner;Greece.jpg;1952
Turkey;Joiner;Turkey.jpg;1952
Germany;Joiner;Germany.jpg;1955
Spain;Joiner;Spain.jpg;1982
Poland;Joiner;Poland.jpg;1999
Czech Republic;Joiner;Czech_Republic.jpg;1999
Hungary;Joiner;Hungary.jpg;1999
Bulgaria;Joiner;Bulgaria.jpg;2004
Estonia;Joiner;Estonia.jpg;2004
Latvia;Joiner;Latvia.jpg;2004
Lithuania;Joiner;Lithuania.jpg;2004
Romania;Joiner;Romania.jpg;2004
Slovakia;Joiner;Slovakia.jpg;2004
Slovenia;Joiner;Slovenia.jpg;2004
Albania;Joiner;Albania.jpg;2009
Croatia;Joiner;Croatia.jpg;2009
Montenegro;Joiner;Montenegro.jpg;2017
North Macedonia;Joiner;North_Macedonia.jpg;2020
Finland;Joiner;Finland.jpg;2023
Sweden;Joiner;Sweden.jpg;2023
"""
    data = [l.split(";") for l in table_data.splitlines()]
    story = fitz.Story(HTML, archive=national_flags)
    body = story.body
    table = body.find("table", None, None)
    template = body.find(None, "id", "template")
    for line in data[1:]:
        country, member, flag, since = line
        row = template.clone()
        row.find(None, "id", "country").add_text(country)
        row.find(None, "id", "member").add_text(member)
        row.find(None, "id", "flag").add_image(flag)
        row.find(None, "id", "since").add_text(since)
        table.append_child(row)
    template.remove()
    return story


report = FrontMatterReport(fitz.paper_rect("letter"))
story = fetch_rows()
items = LongTable(
    report=report,
    story=story,
    top_row="header",
)

report.pages = report.page0 = [items]
report.run("NATO.pdf")

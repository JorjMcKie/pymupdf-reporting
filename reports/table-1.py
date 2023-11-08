import fitz
from Reports import LongTable, FrontMatterReport
import pathlib

html = pathlib.Path("table-1.html").read_text()
report = FrontMatterReport(fitz.paper_rect("a5-l"))
table = LongTable(report, html=html, top_row="header")
report.page0 = report.pages = [table]
report.run("x.pdf")

import pathlib
import fitz

from Reports import SimpleBlock, NColumnsReport

# The following defines the overall report object
mediabox = fitz.paper_rect("letter")  # the only required parameter
report = NColumnsReport(mediabox, columns=2)

# Predefined HTML to define the header for all pages
springer_html = pathlib.Path("springer.html").read_bytes().decode()

hdr_html = pathlib.Path("header.html").read_bytes().decode()
header = SimpleBlock(html=hdr_html)

# Predefined HTML for any information only occurring on page 1
prolog_html = pathlib.Path("prolog.html").read_bytes().decode()
prolog = SimpleBlock(html=prolog_html)

springer_html1 = pathlib.Path("springer.html").read_bytes().decode()
springer1 = SimpleBlock(html=springer_html, archive=".")

# report.sections = [prolog, springer1, header]  # set sections list
report.sections = [springer1]  # set sections list

# This generates the report and saves it to the given path name.
report.run("springer.pdf")

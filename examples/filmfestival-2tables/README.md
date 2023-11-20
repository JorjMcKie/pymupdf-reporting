# Example for PyMuPDF Reporting

This script creates a report about a fictitious film festival.

It extracts data from an SQL database (sqlite3). The database contains two tables:
* films
* actors

The _films_ tables has columns title, director, year and the _actors_ table has columns name and film title.

Two tabular reports are created
1. Report 1 lists all films and names all actors being cast.
2. Report 2 lists all actors together with all the films where they have been cast.
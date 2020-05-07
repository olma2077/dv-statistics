"""dv-parser main entry point."""

from pathlib import Path
from tabula import read_pdf

# Constants
DATA_SOURCE_PATH = 'data sources'


def getFiles():
    """Collect available data sources."""
    files = {}

    files['applied'] = list(Path(DATA_SOURCE_PATH).glob('DV*.pdf'))
    files['selected'] = list(Path(DATA_SOURCE_PATH).glob('*.html'))
    files['issued'] = list(Path(DATA_SOURCE_PATH).glob('FY*.pdf'))

    return files


def parseAppliedData(file, countries):
    """Parse file with DV applied data."""
    # print('parseAppliedData:', file)
    f = read_pdf(files['applied'][0],
                 pages="all",
                 output_format="json",
                 lattice=True,
                 silent=True)
    for x in f:
        for i in x["data"]:
            if '' == i[0]["text"]:
                continue
            if 'Total' in i[0]["text"]:
                continue
            if 'Foreign State' in i[0]["text"]:
                continue
            # print(i[0]['text'])
            countries[i[0]['text']] = {}
    return countries


def parseSelectedData(file, countries):
    """Parse file with DV selected data."""
    print('parseSelectedData:', file)


def parseIssuedData(file, countries):
    """Parse file with DV issued data."""
    print('parseIssuedData:', file)


def parseDvData(files):
    """Parse data from files into dict of countries."""
    # Country is a dict of countries with dict of years with data:
    # {country: {fiscal_year: [entrants, derivatives, selected, issued]}}
    countries = {}
    parser = [parseAppliedData, parseSelectedData, parseIssuedData]

    for i, l in enumerate(list(files.values())):
        for f in l:
            countries = parser[i](f, countries)

    return countries


def exportDvData(countries):
    """Export dict of countries with data into a file."""
    pass


if __name__ == "__main__":
    # Form list of files.
    files = getFiles()

    # Parse files into dictionary.
    countries = parseDvData(files)

    # Export data.
    exportDvData(countries)

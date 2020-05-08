"""dv-parser main entry point."""

from pathlib import Path
from tabula import read_pdf
import pprint


# Constants
DATA_SOURCE_PATH = 'data sources'


def a2i(s):
    """Coverts a string with commas to int if possible, None otherwise."""
    print('Trying to convert', s)
    if isinstance(s, float):
        return None
    try:
        return int(s)
    except ValueError:
        return None if ',' not in s else int(s.replace(',', '_'))


def getFiles():
    """Collect available data sources."""
    files = {}

    files['applied'] = list(Path(DATA_SOURCE_PATH).glob('DV*.pdf'))
    files['selected'] = list(Path(DATA_SOURCE_PATH).glob('*.html'))
    files['issued'] = list(Path(DATA_SOURCE_PATH).glob('FY*.pdf'))

    return files


def parseAppliedData(file, countries):
    """Parse file with DV applied data."""
    print('parseAppliedData:', file)
    df = read_pdf(file,
                  pages="all",
                  lattice=True,
                  silent=True)

    years = [int(x[3:]) for x in df[0].columns if 'FY' in x]

    for line in (line for table in df for line in table.values):
        if isinstance(line[0], float):
            continue
        if 'Foreign' in line[0]:
            continue
        if 'Total' in line[0]:
            continue
        for i, year in enumerate(years):
            countries.setdefault(line[0], {})
            countries[line[0]][year] = [a2i(line[3*i+1]),
                                        a2i(line[3*i+2]),
                                        None,
                                        None]
    return countries


def parseSelectedData(file, countries):
    """Parse file with DV selected data."""
    print('parseSelectedData:', file)
    return countries


def parseIssuedData(file, countries):
    """Parse file with DV issued data."""
    print('parseIssuedData:', file)
    return countries


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
    pprint.pprint(countries)
    # Export data.
    exportDvData(countries)

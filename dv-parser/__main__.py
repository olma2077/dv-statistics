"""dv-parser main entry point."""

from pathlib import Path
import re
from unicodedata import normalize

from tabula import read_pdf
from bs4 import BeautifulSoup


# Constants
DATA_SOURCE_PATH = 'data sources'
START_YEAR = 2007
END_YEAR = 2021


def a2i(s):
    """Coverts a string with commas to int if possible, None otherwise."""
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


def normalizeCountry(country):
    """Fix difference in country names across files."""
    substitute = {
        'Bahamas': 'Bahamas, The',
        'Bosnia & Herzegovina': 'Bosnia And Herzegovina',
        'Cape Verde': 'Cabo Verde',
        'Central African Rep': 'Central African Republic',
        'China-Taiwan': 'Taiwan',
        'Cocos Islands': 'Cocos (Keeling) Islands',
        'Cocos Keeling Islands': 'Cocos (Keeling) Islands',
        'Congo': 'Congo, Republic Of The',
        'Congo-Brazzaville': 'Congo, Republic Of The',
        'Congo-Kinshasa': 'Congo, Democratic Republic Of The',
        'Cote D\'Ivoire': 'Cote D’Ivoire',
        'East Timor': 'Timor-Leste',
        'French Southern & Antarctic Lands':
            'French Southern And Antarctic Lands',
        'French Southern And Antarctic Territories':
            'French Southern And Antarctic Lands',
        'Gambia': 'Gambia, The',
        'Hong Kong Special Admin. Region': 'Hong Kong S.A.R.',
        'Hong Kong Special Administrative Region': 'Hong Kong S.A.R.',
        'Macau Special Admin. Region': 'Macau S.A.R.',
        'Macau Special Administrative Region': 'Macau S.A.R.',
        'Macau': 'Macau S.A.R.',
        'Macedonia': 'North Macedonia',
        'Macedonia, The Former Yugoslav Republic Of': 'North Macedonia',
        'Micronesia, Federated Status Of': 'Micronesia, Federated States Of',
        'Micronesia, Federates States Of': 'Micronesia, Federated States Of',
        'New Calendonia': 'New Caledonia',
        'Nine': 'Niue',
        'North Macedonia, Republic Of': 'North Macedonia',
        'Northen Ireland': 'Northern Ireland',
        'Saint Barthelemy': 'St. Barthelemy',
        'Saint Kitts And Nevis': 'St. Kitts And Nevis',
        'Saint Lucia': 'St. Lucia',
        'Saint Martin': 'St. Martin',
        'Saint Vincent And The Grenadines': 'St. Vincent And The Grenadines',
        'Serbia And Montenegro': 'Montenegro',
        'St. Maarten':  'St. Martin',
        'St. Pierre & Miquelon': 'St. Pierre And Miquelon',
        'Western  Samoa': 'Samoa',
        'Western Samoa': 'Samoa',
    }
    try:
        return substitute[country]
    except KeyError:
        return country


def parseAppliedData(file, countries):
    """Parse file with DV applied data."""
    print('parseAppliedData:', file)
    # return countries
    df = read_pdf(file,
                  pages="all",
                  lattice=True,
                  silent=True)

    years = [int(x[3:]) for x in df[0].columns if 'FY' in x]

    for line in (line for table in df for line in table.values):
        # Skip technical lines
        if isinstance(line[0], float):
            continue
        if 'Foreign' in line[0]:
            continue
        if 'Total' in line[0]:
            continue

        country = normalizeCountry(line[0].title().replace('\r', ' '))
        if country not in countries:
            # Create dict strucuture for new country in dict
            countries[country] = {}
            for year in range(START_YEAR, END_YEAR):
                countries[country][year] = [None, None, None, None]
        for i, year in enumerate(years):
            countries[country][year][0] = a2i(line[3*i+1])
            countries[country][year][1] = a2i(line[3*i+2])

    return countries


def parse_row(row):
    """Parse single row of an html table."""
    # Fix unicode issues
    line = normalize("NFKD", row.get_text().replace('\r', ' '))
    countries = re.findall(r"[a-zA-Z][a-zA-Z\-, ’.&]+[a-zA-Z]", line)
    people = re.findall(r"\d[\d,]*", line)
    line = zip((c.title() for c in countries), (a2i(p) for p in people))
    return tuple(line)


def parseSelectedData(file, countries):
    """Parse file with DV selected data."""
    print('parseSelectedData:', file)
    # return countries
    f = open(file, encoding="utf-8")
    soup = BeautifulSoup(f, "html.parser")

    year = int(re.findall(r'\d{4}', f.name)[0])

    for line in (parse_row(row) for row in soup.find_all('tr')):
        for country, people in line:
            country = normalizeCountry(country)
            if country in countries:
                countries[country][year][2] = people
            else:
                # Something is wrong, this shouldn't happen normally.
                print(country, 'is missing, possible typo in source file.')

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
    # pprint.pprint(countries)
    # Export data.
    exportDvData(countries)

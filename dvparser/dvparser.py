"""dv-parser main module."""

from pathlib import Path
import re
from typing import Optional
from unicodedata import normalize
import json
import datetime
import os

import tabula
from bs4 import BeautifulSoup


# Constants
DATA_SOURCE_PATH = 'data_sources'
START_YEAR = 2007
END_YEAR = datetime.date.today().year
OUT_FILE = 'countries.json'
SHELL_DOWNLOADER = './get_data_sources.sh'


def a2i(string: str) -> Optional[int]:
    """Coverts a string with commas to int if possible, None otherwise."""
    if isinstance(string, float):
        return None
    try:
        return int(string)
    except ValueError:
        return None if ',' not in string else int(string.replace(',', '_'))


def init_data_sources():
    """Quick hack with shell script"""
    os.system(SHELL_DOWNLOADER)


def get_files() -> dict:
    """Collect available data sources."""
    files = {}

    if not Path(DATA_SOURCE_PATH).exists():
        print("Data sources are missing, downloading...")
        init_data_sources()

    files['applied'] = list(Path(DATA_SOURCE_PATH).glob('DV*.pdf'))
    files['selected'] = list(Path(DATA_SOURCE_PATH).glob('*.html'))
    files['issued'] = list(Path(DATA_SOURCE_PATH).glob('FY*.pdf'))

    return files


def normalize_country(country: str) -> str:
    """Fix difference in country names across files."""
    substitute = {
        'Bahamas': 'Bahamas, The',
        'Bosnia & Herzegovina': 'Bosnia And Herzegovina',
        'Cape Verde': 'Cabo Verde',
        'Central African Rep': 'Central African Republic',
        'China-Taiwan': 'Taiwan',
        'China - Taiwan Born': 'Taiwan',
        'Cocos Islands': 'Cocos (Keeling) Islands',
        'Cocos Keeling Islands': 'Cocos (Keeling) Islands',
        'Congo': 'Congo, Republic Of The',
        'Congo-Brazzaville': 'Congo, Republic Of The',
        'Congo-Kinshasa': 'Congo, Democratic Republic Of The',
        'Congo, Dem. Rep. Of The': 'Congo, Democratic Republic Of The',
        'Congo, Democratic': 'Congo, Democratic Republic Of The',
        'Congo, Rep. Of The': 'Congo, Republic Of The',
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


def parse_applied_data(file: str, countries: dict) -> dict:
    """Parse file with DV applied data."""
    print('parseAppliedData:', file)
    dframe = tabula.read_pdf(
        file,
        pages="all",
        lattice=True,
        silent=True)

    years = [int(x[3:]) for x in dframe[0].columns if 'FY' in x]

    # 2021 year file has new region column we have to skip
    offset = False
    for line in (line for table in dframe for line in table.values):
        # Skip technical lines
        if isinstance(line[0], float):
            continue
        if 'Foreign' in line[0]:
            continue
        if 'Total' in line[0]:
            continue
        if 'Region' == line[0]:
            offset = True
            continue

        if offset:
            # Removing Region column
            line = line.tolist()
            line.pop(0)

        country = normalize_country(line[0].title().replace('\r', ' '))
        if country not in countries:
            # Create dict strucuture for new country in dict
            countries[country] = {}
            for year in range(START_YEAR, END_YEAR + 1):
                countries[country][year] = [None, None, None, None]

        for i, year in enumerate(years):
            countries[country][year][0] = a2i(line[3*i+1])
            countries[country][year][1] = a2i(line[3*i+2])

    return countries


def parse_row(row: BeautifulSoup) -> tuple:
    """Parse single row of an html table."""
    # Fix unicode issues
    line = normalize("NFKD", row.get_text().replace('\r', ' '))
    countries = re.findall(r"[a-zA-Z][a-zA-Z\-, ’.&]+[a-zA-Z]", line)
    people = re.findall(r"\d[\d,]*", line)
    line = zip((c.title() for c in countries), (a2i(p) for p in people))
    return tuple(line)


def parse_selected_data(file_name: str, countries: dict) -> dict:
    """Parse file with DV selected data."""
    print('parseSelectedData:', file_name)
    with open(file_name, encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    year = int(re.findall(r'\d{4}', file_name.name)[0])

    for line in (parse_row(row) for row in soup.find_all('tr')):
        for country, people in line:
            country = normalize_country(country)
            if country in countries:
                countries[country][year][2] = people
            else:
                # Something is wrong, this shouldn't happen normally.
                print(country, 'is missing, possible typo in source file.')
                print(line)

    return countries


def parse_issued_data(file_name: str, countries: dict) -> dict:
    """Parse file with DV issued data."""
    print('parseIssuedData:', file_name)
    dframe = tabula.read_pdf(file_name,
                         pages="all",
                         silent=True)

    years = [int(x) for x in dframe[0].columns[1:]]

    for line in (line for table in dframe for line in table.values):
        # Skip technical lines
        if 'Foreign' in line[0]:
            continue
        if 'Total' in line[0].title():
            continue
        if 'South America' in line[0]:
            continue
        if isinstance(line[1], float):
            continue

        country = normalize_country(line[0].title())
        if country in countries:
            for i, year in enumerate(years):
                countries[country][year][3] = a2i(line[i+1])
        else:
            # Something is wrong, this shouldn't happen normally.
            print(country, 'is missing, possible typo in source file.')

    return countries


def parse_dv_data(files: dict) -> dict:
    """Parse data from files into dict of countries.

    Country is a dict of countries with dict of years with data:
    {country: {fiscal_year: [entrants, derivatives, selected, issued]}}
    """
    countries = {}

    parser = [parse_applied_data, parse_selected_data, parse_issued_data]
    for i, flist in enumerate(list(files.values())):
        for file in flist:
            countries = parser[i](file, countries)

    return countries


def export_dv_data(countries: dict):
    """Export dict of countries with data into a file."""
    with open(OUT_FILE, 'w') as file:
        json.dump(countries, file, sort_keys=True)


def main():
    """Start from here."""
    # Form list of files.
    files = get_files()

    # Parse files into dictionary.
    countries = parse_dv_data(files)

    # Export data.
    export_dv_data(countries)


if __name__ == "__main__":
    main()

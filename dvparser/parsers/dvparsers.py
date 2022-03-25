"""dv-parser main module."""

import datetime
import re
from typing import Optional
from unicodedata import normalize

import tabula
from bs4 import BeautifulSoup


START_YEAR = 2007
END_YEAR = datetime.date.today().year


def a2i(string: str) -> Optional[int]:
    """Converts a string with commas to int if possible, None otherwise."""
    if isinstance(string, float):
        return None
    try:
        return int(string)
    except ValueError:
        return None if ',' not in string else int(string.replace(',', '_'))


def normalize_country(country: str) -> str:
    """Fix difference in country names across files."""
    normalized_countries = {
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
        return normalized_countries[country]
    except KeyError:
        return country


def parse_applied_dv(file: str, countries: dict) -> dict:
    """Parse file with DV applied data."""
    print('parse_applied_dv:', file)
    data_frame = tabula.read_pdf(
        file,
        pages="all",
        lattice=True,
        silent=True)

    years = [int(x[3:]) for x in data_frame[0].columns if 'FY' in x]

    # 2021 year file has new region column we have to skip
    offset = False
    for line in (line for table in data_frame for line in table.values):
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


def parse_selected_dv(file: str, countries: dict) -> dict:
    """Parse file with DV selected data."""
    print('parse_selected_dv:', file)
    with open(file, encoding="utf-8") as file_object:
        soup = BeautifulSoup(file_object, "html.parser")

    year = int(re.findall(r'\d{4}', file.name)[0])

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


def parse_issued_dv(file: str, countries: dict) -> dict:
    """Parse file with DV issued data."""
    print('parse_issued_dv:', file)
    data_frame = tabula.read_pdf(file, pages="all", silent=True)

    years = [int(x) for x in data_frame[0].columns[1:]]

    for line in (line for table in data_frame for line in table.values):
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

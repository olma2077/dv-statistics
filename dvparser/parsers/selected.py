"""Parser for selected DV data sources."""

import re
from unicodedata import normalize

from bs4 import BeautifulSoup

from .helper import a2i, normalize_country


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

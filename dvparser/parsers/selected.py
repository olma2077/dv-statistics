"""Parser for selected DV data sources."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable
from unicodedata import normalize

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from pathlib import Path
    from ..datahandlers import CountryData

from ..datahandlers import init_country_data, normalize_country
from .helper import a2i


def get_file_content(file: Path) -> BeautifulSoup:
    with open(file, encoding="utf-8") as file_object:
        soup = BeautifulSoup(file_object, "html.parser")

    return soup


def get_years(file: Path) -> list:
    return [int(re.findall(r'\d{4}', file.name)[0])]


def parse_row(row: BeautifulSoup) -> tuple:
    """Parse single row of an html table."""
    # Fix unicode issues
    line = normalize("NFKD", row.get_text().replace('\r', ' '))
    countries = re.findall(r"[a-zA-Z][a-zA-Z\-, ’.&]+[a-zA-Z]", line)
    people = re.findall(r"\d[\d,]*", line)
    line = zip((c.title() for c in countries), (a2i(p) for p in people))
    return tuple(line)


def get_line(file_content: BeautifulSoup) -> Iterable[list]:
    for line in (parse_row(row) for row in file_content.find_all('tr')):
        for country, people in line:
            yield [country, people]


def get_country(line: list) -> str:
    return normalize_country(line[0])


def set_country_data(country_data: CountryData, years: list, line: list) -> CountryData:
    country_data[years[0]][2] = line[1]
    return country_data


def parse_selected_dv(file: Path, countries: dict) -> dict:
    """Parse file with DV selected data."""
    print('parse_selected_dv:', file)

    file_content = get_file_content(file)

    years = get_years(file)

    for line in get_line(file_content):
        country = get_country(line)
        if country not in countries:
            countries[country] = init_country_data()

        countries[country] = set_country_data(countries[country], years, line)

    return countries

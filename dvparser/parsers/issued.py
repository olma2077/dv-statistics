"""Parser for issued DV data sources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import tabula

if TYPE_CHECKING:
    from pathlib import Path
    from ..countries import CountryData

from ..countries import init_country_data, normalize_country
from .helper import a2i


def get_file_content(file: Path) -> list:
    return tabula.read_pdf(file, pages="all", silent=True)


def get_years(file_content: list) -> list:
    return [int(x) for x in file_content[0].columns[1:]]


def get_line(file_content: list) -> Iterable[list]:
    for line in (line for table in file_content for line in table.values):
        # Skip technical lines
        if 'Foreign' in line[0]:
            continue
        if 'Total' in line[0].title():
            continue
        if 'South America' in line[0]:
            continue
        if isinstance(line[1], float):
            continue

        yield line


def get_country(line: list) -> str:
    return normalize_country(line[0].title())


def set_country_data(country_data: CountryData, years: list, line: list) -> CountryData:
    for i, year in enumerate(years):
        country_data[year][3] = a2i(line[i+1])

    return country_data


def parse_issued_dv(file: Path, countries: dict) -> dict:
    """Parse file with DV issued data."""
    print('parse_issued_dv:', file)
    file_content = get_file_content(file)

    years = get_years(file_content)

    for line in get_line(file_content):
        country = get_country(line)
        if country not in countries:
            countries[country] = init_country_data()

        countries[country] = set_country_data(countries[country], years, line)

    return countries

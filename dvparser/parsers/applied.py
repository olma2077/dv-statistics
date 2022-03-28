"""Parser for applied DV data sources.  """

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import tabula

if TYPE_CHECKING:
    from pathlib import Path
    from ..datahandlers import CountryData

from ..datahandlers import init_country_data, normalize_country
from .helper import a2i


def get_file_content(file: Path) -> list:
    return tabula.read_pdf(
        file,
        pages="all",
        lattice=True,
        silent=True)


def get_years(file_content: list) -> list:
    return [int(x[3:]) for x in file_content[0].columns if 'FY' in x]


def get_line(file_content: list) -> Iterable[list]:
    # 2021 year file has new region column we have to skip
    offset = False
    for line in (line for table in file_content for line in table.values):
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

        yield line


def get_country(line: list) -> str:
    return normalize_country(line[0].title().replace('\r', ' '))


def set_country_data(country_data: CountryData, years: list, line: list) -> CountryData:
    for i, year in enumerate(years):
        country_data[year][0] = a2i(line[3*i+1])
        country_data[year][1] = a2i(line[3*i+2])

    return country_data


def parse_applied_dv(file: Path, countries: dict) -> dict:
    """Parse file with DV applied data."""
    print('parse_applied_dv:', file)
    file_content = get_file_content(file)

    years = get_years(file_content)

    for line in get_line(file_content):
        country = get_country(line)
        if country not in countries:
            countries[country] = init_country_data()

        countries[country] = set_country_data(countries[country], years, line)

    return countries

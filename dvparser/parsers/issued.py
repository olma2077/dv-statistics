"""Parser for issued DV data sources."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import tabula

if TYPE_CHECKING:
    from pathlib import Path
    from ..datahandlers import CountryData

from ..datahandlers import normalize_country
from .helper import a2i
from .parser import Parser


class IssuedDVParser(Parser):
    """Parser implementation for issued DV data sources."""
    def _get_file_content(self, file: Path) -> list:
        return tabula.read_pdf(file, pages="all", silent=True)

    def _get_years(self, file_content: list) -> list:
        return [int(x) for x in file_content[0].columns[1:]]

    def _get_line(self, file_content: list) -> Iterable[list]:
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

    def _get_country(self, line: list) -> str:
        return normalize_country(line[0].title())

    def _set_country_data(self, country_data: CountryData, years: list, line: list) -> CountryData:
        for i, year in enumerate(years):
            country_data[year][3] = a2i(line[i+1])

        return country_data

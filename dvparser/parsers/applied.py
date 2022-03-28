"""Parser for applied DV data sources.  """

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import tabula

if TYPE_CHECKING:
    from pathlib import Path
    from ..datahandlers import CountryData

from ..datahandlers import normalize_country
from .helper import a2i
from .parser import Parser


class AppliedDVParser(Parser):
    def _get_file_content(self, file: Path) -> list:
        return tabula.read_pdf(file, pages='all', lattice=True, silent=True)

    def _get_years(self, file_content: list) -> list:
        return [int(x[3:]) for x in file_content[0].columns if 'FY' in x]

    def _get_line(self, file_content: list) -> Iterable[list]:
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

    def _get_country(self, line: list) -> str:
        return normalize_country(line[0].title().replace('\r', ' '))

    def _set_country_data(self, country_data: CountryData, years: list, line: list) -> CountryData:
        for i, year in enumerate(years):
            country_data[year][0] = a2i(line[3*i+1])
            country_data[year][1] = a2i(line[3*i+2])

        return country_data

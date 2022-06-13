"""Parser for selected DV data sources."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable
from unicodedata import normalize

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from pathlib import Path
    from ..datahandlers import CountryData

from ..datahandlers import normalize_country
from .helper import a2i
from .parser import Parser


class SelectedDVParser(Parser):
    """Parser implementation for selected DV data sources."""
    def _get_file_content(self, file: Path) -> BeautifulSoup:
        with open(file, encoding="utf-8") as file_object:
            soup = BeautifulSoup(file_object, "html.parser")

        return soup

    def _get_years(self, file_content: BeautifulSoup) -> list:
        return [int(re.findall(r'\d{4}', file_content.find('title').get_text())[0])]

    def _parse_row(self, row: BeautifulSoup) -> tuple:
        """Parse single row of an html table."""
        # Fix unicode issues
        line = normalize("NFKD", row.get_text().replace('\r', ' '))
        countries = re.findall(r"[a-zA-Z][a-zA-Z\-, ’.&]+[a-zA-Z]", line)
        people = re.findall(r"\d[\d,]*", line)
        line = zip((c.title() for c in countries), (a2i(p) for p in people))
        return tuple(line)

    def _get_line(self, file_content: BeautifulSoup) -> Iterable[list]:
        for line in (self._parse_row(row) for row in file_content.find_all('tr')):
            for country, people in line:
                yield [country, people]

    def _get_country(self, line: list) -> str:
        return normalize_country(line[0])

    def _set_country_data(self, country_data: CountryData, years: list, line: list) -> CountryData:
        country_data[years[0]][2] = line[1]
        return country_data

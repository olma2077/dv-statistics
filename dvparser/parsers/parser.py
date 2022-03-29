"""Abstract Parser class definition.

Parser defines parsing flow and methods required for implementation
to parse different DV data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable, Any

from ..datahandlers import init_country_data

if TYPE_CHECKING:
    from pathlib import Path

    from ..datahandlers import CountryData, Source


class Parser(ABC):
    """Abstract parser class."""
    @abstractmethod
    def _get_file_content(self, file: Path) -> list:
        pass

    @abstractmethod
    def _get_years(self, file_content: Any) -> list:
        pass

    @abstractmethod
    def _get_line(self, file_content: Any) -> Iterable[list]:
        pass

    @abstractmethod
    def _get_country(self, line: list) -> str:
        pass

    @abstractmethod
    def _set_country_data(self, country_data: CountryData, years: list, line: list) -> CountryData:
        pass

    def parse(self, source: Source, countries: dict[str, CountryData]) -> dict[str, CountryData]:
        """Parse file with DV applied data."""
        print('Parsing', source.type, source.file.name)
        file_content = self._get_file_content(source.file)

        years = self._get_years(file_content)

        for line in self._get_line(file_content):
            country = self._get_country(line)
            if country not in countries:
                countries[country] = init_country_data()

            countries[country] = self._set_country_data(countries[country], years, line)

        return countries

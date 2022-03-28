"""dv-parser main entry point."""

import json
import os
from inspect import getmembers, isfunction
from pathlib import Path

from dvparser import parsers

from .countries import CountryData

DATA_SOURCES_PATH = 'data_sources'
OUTPUT_FILE = 'countries.json'
SHELL_DOWNLOADER = './get_data_sources.sh'

Sources = dict[str, list[Path]]


def download_dv_sources():
    """Quick hack with shell script"""
    os.system(SHELL_DOWNLOADER)


def get_dv_sources() -> Sources:
    """Collect available DV sources."""
    sources: Sources = {}

    if not Path(DATA_SOURCES_PATH).exists():
        print("Data sources are missing, downloading...")
        download_dv_sources()

    sources['applied'] = list(Path(DATA_SOURCES_PATH).glob('DV*.pdf'))
    sources['issued'] = list(Path(DATA_SOURCES_PATH).glob('FY*.pdf'))
    sources['selected'] = list(Path(DATA_SOURCES_PATH).glob('*.html'))

    return sources


def parse_dv_sources(sources: Sources) -> dict[str, CountryData]:
    """Parse data from files into dict of countries.

    Country is a dict of countries with dict of years with data:
    {country: {fiscal_year: [entrants, derivatives, selected, issued]}}
    """
    countries: dict[str, CountryData] = {}
    parser_functions = [item[1] for item in getmembers(parsers, isfunction)]

    for i, files in enumerate(list(sources.values())):
        for file in files:
            # TODO change implicit map of parser to source type to explicit
            countries = parser_functions[i](file, countries)

    return countries


def export_dv_data(countries: dict[str, CountryData]):
    """Export dict of countries with data into a file."""
    with open(OUTPUT_FILE, 'w') as file:
        json.dump(countries, file, sort_keys=True)


def main():
    """Start from here."""
    sources = get_dv_sources()
    countries = parse_dv_sources(sources)
    export_dv_data(countries)


if __name__ == "__main__":
    main()

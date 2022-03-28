"""dv-parser main entry point."""

import json
import os
from pathlib import Path

from dvparser import parsers

from .datahandlers import CountryData, Source

DATA_SOURCES_PATH = 'data_sources'
OUTPUT_FILE = 'countries.json'
SHELL_DOWNLOADER = './get_data_sources.sh'


def download_dv_sources():
    """Quick hack with shell script"""
    os.system(SHELL_DOWNLOADER)


def get_dv_sources() -> list[Source]:
    """Collect available DV sources."""
    sources = []

    if not Path(DATA_SOURCES_PATH).exists():
        print("Data sources are missing, downloading...")
        download_dv_sources()

    sources += [Source('applied', src) for src in list(Path(DATA_SOURCES_PATH).glob('DV*.pdf'))]
    sources += [Source('issued', src) for src in list(Path(DATA_SOURCES_PATH).glob('FY*.pdf'))]
    sources += [Source('selected', src) for src in list(Path(DATA_SOURCES_PATH).glob('*.html'))]

    return sources


def parse_dv_sources(sources: list[Source]) -> dict[str, CountryData]:
    """Parse data from files into dict of countries.

    Country is a dict of countries with dict of years with data:
    {country: {fiscal_year: [entrants, derivatives, selected, issued]}}
    """
    countries: dict[str, CountryData] = {}

    for source in sources:
        countries = parsers.parse_dv_data(source, countries)

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

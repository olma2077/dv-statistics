"""
Parser for issued DV data sources
"""

import tabula

from .helper import a2i, normalize_country


def parse_issued_dv(file: str, countries: dict) -> dict:
    """Parse file with DV issued data."""
    print('parse_issued_dv:', file)
    data_frame = tabula.read_pdf(file, pages="all", silent=True)

    years = [int(x) for x in data_frame[0].columns[1:]]

    for line in (line for table in data_frame for line in table.values):
        # Skip technical lines
        if 'Foreign' in line[0]:
            continue
        if 'Total' in line[0].title():
            continue
        if 'South America' in line[0]:
            continue
        if isinstance(line[1], float):
            continue

        country = normalize_country(line[0].title())
        if country in countries:
            for i, year in enumerate(years):
                countries[country][year][3] = a2i(line[i+1])
        else:
            # Something is wrong, this shouldn't happen normally.
            print(country, 'is missing, possible typo in source file.')

    return countries

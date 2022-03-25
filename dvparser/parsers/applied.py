"""Parser for applied DV data sources."""

import datetime

import tabula

from .helper import a2i, normalize_country

START_YEAR = 2007
END_YEAR = datetime.date.today().year


def parse_applied_dv(file: str, countries: dict) -> dict:
    """Parse file with DV applied data."""
    print('parse_applied_dv:', file)
    data_frame = tabula.read_pdf(
        file,
        pages="all",
        lattice=True,
        silent=True)

    years = [int(x[3:]) for x in data_frame[0].columns if 'FY' in x]

    # 2021 year file has new region column we have to skip
    offset = False
    for line in (line for table in data_frame for line in table.values):
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

        country = normalize_country(line[0].title().replace('\r', ' '))
        if country not in countries:
            # Create dict strucuture for new country in dict
            countries[country] = {}
            for year in range(START_YEAR, END_YEAR + 1):
                countries[country][year] = [None, None, None, None]

        for i, year in enumerate(years):
            countries[country][year][0] = a2i(line[3*i+1])
            countries[country][year][1] = a2i(line[3*i+2])

    return countries

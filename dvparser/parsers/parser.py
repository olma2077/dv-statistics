from ..datahandlers import CountryData, Source
from .applied import parse_applied_dv
from .issued import parse_issued_dv
from .selected import parse_selected_dv


def parse_dv_data(source: Source, countries: dict[str, CountryData]) -> dict[str, CountryData]:
    """Parse data from files into dict of countries.

    Country is a dict of countries with dict of years with data:
    {country: {fiscal_year: [entrants, derivatives, selected, issued]}}
    """
    if source.type == 'applied':
        countries = parse_applied_dv(source.file, countries)
    elif source.type == 'issued':
        countries = parse_issued_dv(source.file, countries)
    elif source.type == 'selected':
        countries = parse_selected_dv(source.file, countries)
    else:
        raise ValueError(f'Unknown source type {source.type}')

    return countries

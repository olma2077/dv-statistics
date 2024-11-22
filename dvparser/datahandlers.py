"""Countries-related stuff."""
from __future__ import annotations

import datetime
import dataclasses
from enum import Enum
from json import JSONEncoder
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pathlib import Path

START_YEAR = 2007
END_YEAR = datetime.date.today().year


@dataclasses.dataclass
class YearData():
    """Applicants data for a given year."""
    entrants: Optional[int] = None
    derivatives: Optional[int] = None
    selected: Optional[int] = None
    issued: Optional[int] = None


CountryData = dict[int, YearData]


class SourceType(Enum):
    """Type of DV source file."""
    APPLIED = 1
    SELECTED = 2
    ISSUED = 3


@dataclasses.dataclass
class Source:
    """DV data source file with its type."""
    type: SourceType
    file: Path


class EnhancedJSONEncoder(JSONEncoder):
    """Custom parser for dataclasses"""
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def normalize_country(country: str) -> str:
    """Fix difference in country names across files."""
    normalized_countries = {
        'Bahamas': 'Bahamas, The',
        'Bosnia & Herzegovina': 'Bosnia And Herzegovina',
        'Cape Verde': 'Cabo Verde',
        'Central African Rep': 'Central African Republic',
        'China-Taiwan': 'Taiwan',
        'China - Taiwan Born': 'Taiwan',
        'Cocos Islands': 'Cocos (Keeling) Islands',
        'Cocos Keeling Islands': 'Cocos (Keeling) Islands',
        'Congo': 'Congo, Republic Of The',
        'Congo-Brazzaville': 'Congo, Republic Of The',
        'Congo-Kinshasa': 'Congo, Democratic Republic Of The',
        'Congo, Dem. Rep. Of The': 'Congo, Democratic Republic Of The',
        'Congo, Democratic': 'Congo, Democratic Republic Of The',
        'Congo, Rep. Of The': 'Congo, Republic Of The',
        'Cote D\'Ivoire': 'Cote D’Ivoire',
        'East Timor': 'Timor-Leste',
        'French Southern & Antarctic Lands':
            'French Southern And Antarctic Lands',
        'French Southern And Antarctic Territories':
            'French Southern And Antarctic Lands',
        'Gambia': 'Gambia, The',
        'Hong Kong Special Admin. Region': 'Hong Kong S.A.R.',
        'Hong Kong Special Administrative Region': 'Hong Kong S.A.R.',
        'Macau Special Admin. Region': 'Macau S.A.R.',
        'Macau Special Administrative Region': 'Macau S.A.R.',
        'Macau': 'Macau S.A.R.',
        'Macedonia': 'North Macedonia',
        'Macedonia, The Former Yugoslav Republic Of': 'North Macedonia',
        'Micronesia, Federated Status Of': 'Micronesia, Federated States Of',
        'Micronesia, Federates States Of': 'Micronesia, Federated States Of',
        'New Calendonia': 'New Caledonia',
        'Nine': 'Niue',
        'North Macedonia, Republic Of': 'North Macedonia',
        'Northen Ireland': 'Northern Ireland',
        'Saint Barthelemy': 'St. Barthelemy',
        'Saint Kitts And Nevis': 'St. Kitts And Nevis',
        'Saint Lucia': 'St. Lucia',
        'Saint Martin': 'St. Martin',
        'Saint Vincent And The Grenadines': 'St. Vincent And The Grenadines',
        'Serbia And Montenegro': 'Montenegro',
        'St. Maarten':  'St. Martin',
        'St. Pierre & Miquelon': 'St. Pierre And Miquelon',
        'Western  Samoa': 'Samoa',
        'Western Samoa': 'Samoa',
    }

    try:
        return normalized_countries[country]
    except KeyError:
        return country


def init_country_data() -> CountryData:
    """Initialize country data structure."""
    return {year: YearData() for year in range(START_YEAR, END_YEAR)}

"""Common helper functions for DV parsers."""

from typing import Optional


def a2i(string: str) -> Optional[int]:
    """Converts a string with commas to int if possible, None otherwise."""
    if isinstance(string, float):
        return None

    try:
        return int(string)
    except ValueError:
        return None if ',' not in string else int(string.replace(',', '_'))

"""Parsers module for different formats of DV data sources."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .applied import AppliedDVParser
from .issued import IssuedDVParser
from .selected import SelectedDVParser

if TYPE_CHECKING:
    from .parser import Parser
    from ..datahandlers import Source


def get_parser(source: Source) -> Parser:
    """Get parser for given DV data source."""
    if source.type == "applied":
        return AppliedDVParser()
    elif source.type == "issued":
        return IssuedDVParser()
    elif source.type == "selected":
        return SelectedDVParser()
    else:
        raise ValueError(f"Unknown DV data source: {source.type}")


__all__ = ['get_parser']

"""Parsers module for different formats of DV data sources."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datahandlers import SourceType
from .applied import AppliedDVParser
from .issued import IssuedDVParser
from .selected import SelectedDVParser

if TYPE_CHECKING:
    from ..datahandlers import Source
    from .parser import Parser


def get_parser(source: Source) -> Parser:
    """Get parser for given DV data source."""
    if source.type == SourceType.APPLIED:
        return AppliedDVParser()
    if source.type == SourceType.ISSUED:
        return IssuedDVParser()
    if source.type == SourceType.SELECTED:
        return SelectedDVParser()

    raise ValueError(f"Unknown DV data source: {source.type}")


__all__ = ['get_parser']

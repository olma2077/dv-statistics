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
    match source.type:
        case SourceType.APPLIED:
            return AppliedDVParser()
        case SourceType.ISSUED:
            return IssuedDVParser()
        case SourceType.SELECTED:
            return SelectedDVParser()

    raise ValueError(f"Unknown DV data source: {source.type}")


__all__ = ["get_parser"]

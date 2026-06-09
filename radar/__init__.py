"""Core package exports for AI Release Radar."""

from radar.models import DiffResult, Item, RunIndexEntry, SourceSnapshot
from radar.parsers import (
    parse_json_items_fixture,
    parse_simple_html_release_fixture,
    parse_simple_text_release_fixture,
)
from radar.snapshot_builder import build_source_snapshot_from_items

__all__ = [
    "DiffResult",
    "Item",
    "RunIndexEntry",
    "SourceSnapshot",
    "build_source_snapshot_from_items",
    "parse_json_items_fixture",
    "parse_simple_html_release_fixture",
    "parse_simple_text_release_fixture",
]

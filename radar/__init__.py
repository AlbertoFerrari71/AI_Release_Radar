"""Core package exports for AI Release Radar."""

from radar.classification import (
    ItemClassification,
    classify_category_from_text,
    classify_item,
    classify_severity_from_text,
)
from radar.models import DiffResult, Item, RunIndexEntry, SourceSnapshot
from radar.offline_workflow import (
    build_diff_from_snapshot_files,
    build_snapshot_and_diff_from_item_fixtures,
    load_items_fixture_snapshot,
    read_diff_result,
    read_snapshot,
    write_diff_result,
    write_snapshot,
)
from radar.parsers import (
    parse_json_items_fixture,
    parse_simple_html_release_fixture,
    parse_simple_text_release_fixture,
)
from radar.scoring import RelevanceScore, score_diff_items, score_item
from radar.snapshot_builder import build_source_snapshot_from_items

__all__ = [
    "DiffResult",
    "Item",
    "ItemClassification",
    "RelevanceScore",
    "RunIndexEntry",
    "SourceSnapshot",
    "build_diff_from_snapshot_files",
    "build_snapshot_and_diff_from_item_fixtures",
    "build_source_snapshot_from_items",
    "classify_category_from_text",
    "classify_item",
    "classify_severity_from_text",
    "load_items_fixture_snapshot",
    "parse_json_items_fixture",
    "parse_simple_html_release_fixture",
    "parse_simple_text_release_fixture",
    "read_diff_result",
    "read_snapshot",
    "score_diff_items",
    "score_item",
    "write_diff_result",
    "write_snapshot",
]

"""Core package exports for AI Release Radar."""

from radar.classification import (
    ItemClassification,
    classify_category_from_text,
    classify_item,
    classify_severity_from_text,
)
from radar.models import DiffResult, Item, RunIndexEntry, SourceSnapshot
from radar.live_url_check import (
    check_sources_live,
    review_live_check_results,
    summarize_url_verification_results,
    verification_results_to_dict,
)
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
from radar.project_impact import (
    ProjectImpact,
    impact_item_for_projects,
    impact_scores_for_projects,
    load_project_map,
)
from radar.report_engine import (
    ReportInput,
    load_report_input,
    render_compact_markdown_report,
    render_full_markdown_report,
    render_report_status,
)
from radar.scoring import RelevanceScore, score_diff_items, score_item
from radar.source_registry import (
    SourceDefinition,
    load_source_registry,
    load_source_registry_file,
    source_registry_to_dict,
    validate_source_definition,
)
from radar.source_fetcher import (
    FetchedSourceContent,
    fetched_sources_to_dict,
    fetch_source_content,
    fetch_sources_content,
    summarize_fetched_sources,
)
from radar.snapshot_builder import build_source_snapshot_from_items
from radar.url_verifier import UrlVerificationResult, verify_url_format, verify_url_live

__all__ = [
    "DiffResult",
    "FetchedSourceContent",
    "Item",
    "ItemClassification",
    "ProjectImpact",
    "ReportInput",
    "RelevanceScore",
    "RunIndexEntry",
    "SourceDefinition",
    "SourceSnapshot",
    "UrlVerificationResult",
    "build_diff_from_snapshot_files",
    "build_snapshot_and_diff_from_item_fixtures",
    "build_source_snapshot_from_items",
    "check_sources_live",
    "classify_category_from_text",
    "classify_item",
    "classify_severity_from_text",
    "fetched_sources_to_dict",
    "fetch_source_content",
    "fetch_sources_content",
    "impact_item_for_projects",
    "impact_scores_for_projects",
    "load_source_registry",
    "load_source_registry_file",
    "load_report_input",
    "load_project_map",
    "load_items_fixture_snapshot",
    "parse_json_items_fixture",
    "parse_simple_html_release_fixture",
    "parse_simple_text_release_fixture",
    "read_diff_result",
    "read_snapshot",
    "render_compact_markdown_report",
    "render_full_markdown_report",
    "render_report_status",
    "review_live_check_results",
    "score_diff_items",
    "score_item",
    "source_registry_to_dict",
    "summarize_fetched_sources",
    "summarize_url_verification_results",
    "validate_source_definition",
    "verification_results_to_dict",
    "verify_url_format",
    "verify_url_live",
    "write_diff_result",
    "write_snapshot",
]

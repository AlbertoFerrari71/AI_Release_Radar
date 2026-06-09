"""Offline fixture-to-snapshot-to-diff workflow helpers."""

from __future__ import annotations

from pathlib import Path

from radar.diff import diff_snapshots
from radar.json_utils import read_json, write_json
from radar.models import DiffResult, SourceSnapshot
from radar.parsers import parse_json_items_fixture
from radar.snapshot_builder import build_source_snapshot_from_items


def load_items_fixture_snapshot(
    fixture_path: str,
    source_id: str,
    provider: str,
    fetched_at: str,
    page_hash: str | None = None,
) -> SourceSnapshot:
    """Load a JSON item fixture and build an offline SourceSnapshot."""
    fixture_data = read_json(Path(fixture_path))
    items = parse_json_items_fixture(source_id, provider, fixture_data)
    return build_source_snapshot_from_items(
        source_id=source_id,
        provider=provider,
        fetched_at=fetched_at,
        fetch_status="offline_fixture",
        http_status=None,
        items=items,
        page_hash=page_hash,
    )


def write_snapshot(path: str, snapshot: SourceSnapshot) -> None:
    """Write a SourceSnapshot as deterministic JSON."""
    if not isinstance(snapshot, SourceSnapshot):
        raise ValueError("snapshot must be a SourceSnapshot.")
    write_json(Path(path), snapshot)


def read_snapshot(path: str) -> SourceSnapshot:
    """Read a SourceSnapshot from deterministic JSON."""
    return SourceSnapshot.from_dict(read_json(Path(path)))


def write_diff_result(path: str, diff_result: DiffResult) -> None:
    """Write a DiffResult as deterministic JSON."""
    if not isinstance(diff_result, DiffResult):
        raise ValueError("diff_result must be a DiffResult.")
    write_json(Path(path), diff_result)


def read_diff_result(path: str) -> DiffResult:
    """Read a DiffResult from deterministic JSON."""
    return DiffResult.from_dict(read_json(Path(path)))


def build_diff_from_snapshot_files(
    previous_snapshot_path: str | None,
    current_snapshot_path: str,
) -> DiffResult:
    """Build a DiffResult from snapshot files, with optional previous snapshot."""
    previous = read_snapshot(previous_snapshot_path) if previous_snapshot_path is not None else None
    current = read_snapshot(current_snapshot_path)
    return diff_snapshots(previous, current)


def build_snapshot_and_diff_from_item_fixtures(
    previous_fixture_path: str | None,
    current_fixture_path: str,
    source_id: str,
    provider: str,
    previous_fetched_at: str | None,
    current_fetched_at: str,
    previous_page_hash: str | None = None,
    current_page_hash: str | None = None,
) -> tuple[SourceSnapshot | None, SourceSnapshot, DiffResult]:
    """Build previous/current snapshots and diff directly from JSON fixtures."""
    previous_snapshot: SourceSnapshot | None = None
    if previous_fixture_path is not None:
        if previous_fetched_at is None:
            raise ValueError("previous_fetched_at is required when previous_fixture_path is set.")
        previous_snapshot = load_items_fixture_snapshot(
            previous_fixture_path,
            source_id,
            provider,
            previous_fetched_at,
            previous_page_hash,
        )

    current_snapshot = load_items_fixture_snapshot(
        current_fixture_path,
        source_id,
        provider,
        current_fetched_at,
        current_page_hash,
    )
    return previous_snapshot, current_snapshot, diff_snapshots(previous_snapshot, current_snapshot)

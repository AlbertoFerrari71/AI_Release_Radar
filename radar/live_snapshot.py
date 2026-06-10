"""Controlled live snapshot generation with explicit outside-repo outputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from radar.hash_utils import stable_sha256_text
from radar.json_utils import write_json
from radar.models import RunIndexEntry, SourceSnapshot
from radar.parsers import (
    parse_codex_changelog_fixture,
    parse_github_releases_api_fixture,
)
from radar.run_index import append_run_index_entry
from radar.snapshot_builder import build_source_snapshot_from_items
from radar.source_fetcher import FetchedSourceContent, fetch_sources_content
from radar.source_registry import SourceDefinition, load_source_registry_file


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_SUMMARY_FILENAME = "0170-Live_Snapshot_Run_Summary.json"
RUN_INDEX_ENTRY_FILENAME = "0170-Live_Snapshot_Run_Index_Entry.json"
RUNS_INDEX_FILENAME = "runs_index.jsonl"

FetchSourcesCallable = Callable[
    [list[SourceDefinition], float | None, int | None, int],
    list[FetchedSourceContent],
]


@dataclass(frozen=True)
class LiveSnapshotRunResult:
    """Serializable result for one controlled live snapshot run."""

    run_id: str
    status: str
    output_dir: str
    source_count: int
    snapshot_count: int
    parsed_count: int
    skipped_count: int
    failed_count: int
    snapshot_paths: list[str]
    run_summary_path: str
    run_index_entry_path: str
    runs_index_path: str
    source_diagnostics: list[dict[str, Any]]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "output_dir": self.output_dir,
            "source_count": self.source_count,
            "snapshot_count": self.snapshot_count,
            "parsed_count": self.parsed_count,
            "skipped_count": self.skipped_count,
            "failed_count": self.failed_count,
            "snapshot_paths": list(self.snapshot_paths),
            "run_summary_path": self.run_summary_path,
            "run_index_entry_path": self.run_index_entry_path,
            "runs_index_path": self.runs_index_path,
            "source_diagnostics": [dict(source) for source in self.source_diagnostics],
            "errors": list(self.errors),
        }


def run_live_snapshot(
    *,
    source_registry: str,
    output_dir: str,
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int = 65536,
    run_id: str | None = None,
    fetched_at: str | None = None,
    fetcher: FetchSourcesCallable = fetch_sources_content,
) -> LiveSnapshotRunResult:
    """Run an explicit controlled fetch/parse/snapshot workflow."""
    target_dir = _outside_repo_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    run_timestamp = fetched_at if fetched_at is not None else _utc_now_iso()
    effective_run_id = run_id if run_id is not None else _run_id_from_timestamp(run_timestamp)

    sources = _select_enabled_sources(load_source_registry_file(source_registry), max_sources)
    fetch_results = fetcher(sources, timeout_seconds, None, max_bytes)
    fetched_by_source_id = {result.source_id: result for result in fetch_results}

    snapshots: list[SourceSnapshot] = []
    snapshot_paths: list[str] = []
    source_summaries: list[dict[str, Any]] = []
    errors: list[str] = []
    parsed_count = 0
    skipped_count = 0
    failed_count = 0

    for source in sources:
        fetched = fetched_by_source_id.get(source.source_id)
        if fetched is None:
            failed_count += 1
            error = f"{source.source_id}: missing fetch result"
            errors.append(error)
            source_summaries.append(_source_summary(source, None, "fetch_missing", 0, error))
            continue

        items, parser_status, parser_error = _parse_fetched_source(source, fetched, run_timestamp)
        if fetched.ok and parser_status == "parsed":
            parsed_count += 1
        elif fetched.ok:
            skipped_count += 1
        else:
            failed_count += 1
        if parser_error is not None:
            errors.append(f"{source.source_id}: {parser_error}")

        snapshot = build_source_snapshot_from_items(
            source_id=source.source_id,
            provider=source.provider,
            fetched_at=fetched.fetched_at or run_timestamp,
            fetch_status=_snapshot_fetch_status(fetched, parser_status),
            http_status=fetched.http_status_code or fetched.status_code,
            items=items,
            page_hash=stable_sha256_text(fetched.body_sample) if fetched.body_sample else None,
        )
        snapshot_path = target_dir / f"0170-Snapshot_{source.source_id}.json"
        write_json(snapshot_path, snapshot)
        snapshots.append(snapshot)
        snapshot_paths.append(str(snapshot_path))
        source_summaries.append(
            _source_summary(source, fetched, parser_status, len(items), parser_error)
        )

    run_status = _run_status(
        source_count=len(sources),
        failed_count=failed_count,
        errors=errors,
    )
    run_index_entry = RunIndexEntry(
        run_id=effective_run_id,
        step="0170",
        status=run_status,
        started_at=run_timestamp,
        finished_at=run_timestamp,
        duration_seconds=0.0,
        report_full=None,
        report_compact=None,
        snapshot_dir=str(target_dir),
        notes="Controlled live snapshot generation output. No LAST-* or latest-* files.",
    )
    run_index_entry_path = target_dir / RUN_INDEX_ENTRY_FILENAME
    runs_index_path = target_dir / RUNS_INDEX_FILENAME
    write_json(run_index_entry_path, run_index_entry)
    append_run_index_entry(runs_index_path, run_index_entry)

    result = LiveSnapshotRunResult(
        run_id=effective_run_id,
        status=run_status,
        output_dir=str(target_dir),
        source_count=len(sources),
        snapshot_count=len(snapshots),
        parsed_count=parsed_count,
        skipped_count=skipped_count,
        failed_count=failed_count,
        snapshot_paths=snapshot_paths,
        run_summary_path=str(target_dir / RUN_SUMMARY_FILENAME),
        run_index_entry_path=str(run_index_entry_path),
        runs_index_path=str(runs_index_path),
        source_diagnostics=source_summaries,
        errors=errors,
    )
    write_json(
        target_dir / RUN_SUMMARY_FILENAME,
        {
            "schema_version": 1,
            "run": result.to_dict(),
            "sources": source_summaries,
        },
    )
    return result


def _outside_repo_output_dir(output_dir: str) -> Path:
    target_dir = Path(output_dir).expanduser().resolve()
    if _is_path_within(target_dir, REPO_ROOT):
        raise ValueError("live-snapshot output_dir must be outside repository.")
    if target_dir.name.startswith("LAST-") or target_dir.name.startswith("latest-"):
        raise ValueError("live-snapshot output_dir must not use LAST-* or latest-* names.")
    return target_dir


def _select_enabled_sources(
    sources: list[SourceDefinition],
    max_sources: int | None,
) -> list[SourceDefinition]:
    enabled = [source for source in sources if source.live_check_enabled]
    if max_sources is None:
        return enabled
    if not isinstance(max_sources, int) or isinstance(max_sources, bool) or max_sources < 1:
        raise ValueError("max_sources must be a positive integer or None.")
    return enabled[:max_sources]


def _parse_fetched_source(
    source: SourceDefinition,
    fetched: FetchedSourceContent,
    first_seen: str,
) -> tuple[list, str, str | None]:
    if not fetched.ok:
        return [], "fetch_failed", fetched.error_code or fetched.error
    if fetched.truncated:
        return [], "parser_skipped_truncated", None
    if not fetched.body_sample:
        return [], "parser_skipped_no_content", None
    try:
        if source.source_type == "github_api":
            data = json.loads(fetched.body_sample)
            return (
                parse_github_releases_api_fixture(
                    source.source_id,
                    source.provider,
                    data,
                    first_seen=first_seen,
                ),
                "parsed",
                None,
            )
        if (
            source.source_id == "openai_codex_changelog"
            and fetched.content_type in {"text/markdown", "text/plain"}
        ):
            return (
                parse_codex_changelog_fixture(
                    source.source_id,
                    source.provider,
                    fetched.body_sample,
                    first_seen=first_seen,
                    source_url=source.url,
                ),
                "parsed",
                None,
            )
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        return [], "parser_failed", str(exc)
    return [], "parser_skipped_unsupported_source", None


def _snapshot_fetch_status(fetched: FetchedSourceContent, parser_status: str) -> str:
    if not fetched.ok:
        return "fetch_failed"
    return f"fetch_ok_{parser_status}"


def _source_summary(
    source: SourceDefinition,
    fetched: FetchedSourceContent | None,
    parser_status: str,
    item_count: int,
    error: str | None,
) -> dict[str, Any]:
    return {
        "source_id": source.source_id,
        "provider": source.provider,
        "source_type": source.source_type,
        "fetch_status": fetched.status if fetched is not None else "missing",
        "http_status_code": (
            fetched.http_status_code or fetched.status_code if fetched is not None else None
        ),
        "parser_status": parser_status,
        "item_count": item_count,
        "error": error,
    }


def _run_status(*, source_count: int, failed_count: int, errors: list[str]) -> str:
    if source_count == 0:
        return "empty"
    if failed_count == 0 and not errors:
        return "success"
    return "partial"


def _run_id_from_timestamp(timestamp: str) -> str:
    safe = (
        timestamp.replace(":", "")
        .replace("-", "")
        .replace("T", "-")
        .replace("Z", "Z")
    )
    return f"0170-{safe}"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True

"""Manual first real radar report workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from radar.classification import classify_item
from radar.diff import diff_snapshots
from radar.json_utils import read_json, write_json
from radar.live_snapshot import FetchSourcesCallable, run_live_snapshot
from radar.models import RunIndexEntry, SourceSnapshot
from radar.project_impact import impact_scores_for_projects, load_project_map
from radar.report_engine import ReportInput, render_report_status
from radar.run_index import append_run_index_entry
from radar.scoring import score_diff_items
from radar.source_fetcher import fetch_sources_content


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT_MAP_PATH = REPO_ROOT / "examples" / "fixtures" / "0070_project_map.json"
REPORT_FULL_FILENAME = "0180-Report_Full.md"
REPORT_COMPACT_FILENAME = "0180-Report_Compact.md"
RUN_SUMMARY_FILENAME = "0180-Run_Summary.json"
RUN_INDEX_ENTRY_FILENAME = "0180-Run_Index_Entry.json"
RUNS_INDEX_FILENAME = "runs_index.jsonl"
COMBINED_SOURCE_ID = "0180_real_radar_run"
COMBINED_PROVIDER = "mixed"
DEFAULT_REAL_RUN_MAX_BYTES = 5 * 1024 * 1024
NO_PARSED_ITEMS_STATUS = "NO_PARSED_ITEMS"


@dataclass(frozen=True)
class RealRadarRunResult:
    """Serializable result for one manual real radar run."""

    run_id: str
    status: str
    output_dir: str
    report_full: str
    report_compact: str
    run_summary: str
    run_index_entry: str
    runs_index: str
    live_snapshot_status: str
    source_count: int
    parsed_count: int
    skipped_count: int
    failed_count: int
    item_count: int
    new_count: int
    changed_count: int
    removed_count: int
    unchanged_count: int
    project_impact_count: int
    source_diagnostics: list[dict[str, Any]]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "output_dir": self.output_dir,
            "report_full": self.report_full,
            "report_compact": self.report_compact,
            "run_summary": self.run_summary,
            "run_index_entry": self.run_index_entry,
            "runs_index": self.runs_index,
            "live_snapshot_status": self.live_snapshot_status,
            "source_count": self.source_count,
            "parsed_count": self.parsed_count,
            "skipped_count": self.skipped_count,
            "failed_count": self.failed_count,
            "item_count": self.item_count,
            "new_count": self.new_count,
            "changed_count": self.changed_count,
            "removed_count": self.removed_count,
            "unchanged_count": self.unchanged_count,
            "project_impact_count": self.project_impact_count,
            "source_diagnostics": [dict(source) for source in self.source_diagnostics],
            "notes": list(self.notes),
        }


def run_real_radar_report(
    *,
    source_registry: str,
    output_dir: str,
    project_map: str | None = None,
    previous_snapshot_dir: str | None = None,
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int = DEFAULT_REAL_RUN_MAX_BYTES,
    run_id: str | None = None,
    generated_at: str | None = None,
    fetcher: FetchSourcesCallable = fetch_sources_content,
) -> RealRadarRunResult:
    """Run live snapshot generation and produce the first manual radar report."""
    target_dir = _outside_repo_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = generated_at if generated_at is not None else _utc_now_iso()
    effective_run_id = run_id if run_id is not None else _run_id_from_timestamp(timestamp)

    live_result = run_live_snapshot(
        source_registry=source_registry,
        output_dir=str(target_dir),
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
        max_bytes=max_bytes,
        run_id=f"0170-for-{effective_run_id}",
        fetched_at=timestamp,
        fetcher=fetcher,
    )
    current_snapshot = _combined_snapshot_from_paths(
        live_result.snapshot_paths,
        fetched_at=timestamp,
    )
    previous_snapshot = (
        _combined_snapshot_from_dir(previous_snapshot_dir, fetched_at=timestamp)
        if previous_snapshot_dir is not None
        else None
    )
    diff_result = diff_snapshots(previous_snapshot, current_snapshot)
    items_by_id = {item.item_id: item for item in current_snapshot.items}
    classifications_by_id = {
        item_id: classify_item(item) for item_id, item in sorted(items_by_id.items())
    }
    scores = score_diff_items(items_by_id, diff_result, classifications_by_id)
    scores_by_id = {score.item_id: score for score in scores}
    project_map_path = Path(project_map) if project_map is not None else DEFAULT_PROJECT_MAP_PATH
    impacts = impact_scores_for_projects(
        items_by_id,
        classifications_by_id,
        scores,
        load_project_map(read_json(project_map_path)),
    )
    notes = _run_notes(live_result.status, previous_snapshot is None)
    report_input = ReportInput(
        run_id=effective_run_id,
        generated_at=timestamp,
        source_id=current_snapshot.source_id,
        provider=current_snapshot.provider,
        diff_result=diff_result,
        items_by_id=items_by_id,
        classifications_by_id=classifications_by_id,
        scores_by_id=scores_by_id,
        project_impacts=impacts,
        notes=notes,
    )
    live_result_data = live_result.to_dict()
    source_diagnostics = list(live_result_data.get("source_diagnostics", []))
    report_status = _real_report_status(report_input, live_result_data)

    full_report_path = target_dir / REPORT_FULL_FILENAME
    compact_report_path = target_dir / REPORT_COMPACT_FILENAME
    run_summary_path = target_dir / RUN_SUMMARY_FILENAME
    run_index_entry_path = target_dir / RUN_INDEX_ENTRY_FILENAME
    runs_index_path = target_dir / RUNS_INDEX_FILENAME

    _write_text(
        full_report_path,
        _render_real_full_report(
            report_input,
            live_result_data,
            report_status,
            source_diagnostics,
        ),
    )
    _write_text(
        compact_report_path,
        _render_real_compact_report(report_input, live_result_data, report_status),
    )

    run_index_entry = RunIndexEntry(
        run_id=effective_run_id,
        step="0180",
        status=report_status,
        started_at=timestamp,
        finished_at=timestamp,
        duration_seconds=0.0,
        report_full=str(full_report_path),
        report_compact=str(compact_report_path),
        snapshot_dir=str(target_dir),
        notes="First manual real radar report. Runtime outputs are outside repository.",
    )
    write_json(run_index_entry_path, run_index_entry)
    append_run_index_entry(runs_index_path, run_index_entry)

    result = RealRadarRunResult(
        run_id=effective_run_id,
        status=report_status,
        output_dir=str(target_dir),
        report_full=str(full_report_path),
        report_compact=str(compact_report_path),
        run_summary=str(run_summary_path),
        run_index_entry=str(run_index_entry_path),
        runs_index=str(runs_index_path),
        live_snapshot_status=live_result.status,
        source_count=live_result.source_count,
        parsed_count=live_result.parsed_count,
        skipped_count=live_result.skipped_count,
        failed_count=live_result.failed_count,
        item_count=len(current_snapshot.items),
        new_count=len(diff_result.new_items),
        changed_count=len(diff_result.changed_items),
        removed_count=len(diff_result.removed_items),
        unchanged_count=diff_result.unchanged_count,
        project_impact_count=len(impacts),
        source_diagnostics=source_diagnostics,
        notes=notes,
    )
    write_json(
        run_summary_path,
        {
            "schema_version": 1,
            "result": result.to_dict(),
            "live_snapshot": live_result_data,
            "source_diagnostics": source_diagnostics,
            "diff_result": diff_result.to_dict(),
            "report_status": report_status,
        },
    )
    return result


def _real_report_status(report_input: ReportInput, live_result: dict[str, Any]) -> str:
    source_count = live_result.get("source_count")
    parsed_count = live_result.get("parsed_count")
    if isinstance(source_count, int) and source_count > 0 and parsed_count == 0:
        return NO_PARSED_ITEMS_STATUS
    return render_report_status(report_input)


def _combined_snapshot_from_paths(
    snapshot_paths: list[str],
    *,
    fetched_at: str,
) -> SourceSnapshot:
    snapshots = [SourceSnapshot.from_dict(read_json(path)) for path in sorted(snapshot_paths)]
    items = [item for snapshot in snapshots for item in snapshot.items]
    return SourceSnapshot(
        source_id=COMBINED_SOURCE_ID,
        provider=COMBINED_PROVIDER,
        fetched_at=fetched_at,
        fetch_status="combined_live_snapshot",
        http_status=None,
        items=items,
        page_hash=None,
    )


def _combined_snapshot_from_dir(path: str, *, fetched_at: str) -> SourceSnapshot:
    snapshot_dir = Path(path).expanduser().resolve()
    snapshot_paths = sorted(str(candidate) for candidate in snapshot_dir.glob("0170-Snapshot_*.json"))
    if not snapshot_paths:
        raise ValueError("previous_snapshot_dir does not contain 0170-Snapshot_*.json files.")
    return _combined_snapshot_from_paths(snapshot_paths, fetched_at=fetched_at)


def _run_notes(live_status: str, first_observation: bool) -> list[str]:
    notes = [
        f"live snapshot status: {live_status}",
        "runtime outputs stored outside repository",
        "no scheduler activated",
        "no LLM call performed",
    ]
    if first_observation:
        notes.append("baseline / first observation: no previous snapshot provided")
    else:
        notes.append("diff compared with previous snapshot directory")
    return notes


def _render_real_full_report(
    report_input: ReportInput,
    live_result: dict[str, Any],
    report_status: str,
    source_diagnostics: list[dict[str, Any]],
) -> str:
    lines = [
        f"# AI Release Radar Real Report - {report_input.run_id}",
        "",
        "## 1. Executive Summary",
        "",
        f"- [F] Report status: {report_status}.",
        f"- [F] Generated at: {report_input.generated_at}.",
        f"- [F] Sources checked: {live_result.get('source_count')}.",
        f"- [F] Live snapshot status: {live_result.get('status')}.",
        f"- [F] Items found: {len(report_input.items_by_id)}.",
        (
            "- [F] Diff: "
            f"{len(report_input.diff_result.new_items)} new, "
            f"{len(report_input.diff_result.changed_items)} changed, "
            f"{len(report_input.diff_result.removed_items)} removed, "
            f"{report_input.diff_result.unchanged_count} unchanged."
        ),
        "",
        "## 1.1 Run Notes",
        "",
        *[f"- [F] {note}." for note in report_input.notes],
        "",
        "## 2. Sources Controlled",
        "",
        f"- [F] Snapshot files: {len(live_result.get('snapshot_paths', []))}.",
        f"- [F] Parsed sources: {live_result.get('parsed_count')}.",
        f"- [F] Skipped sources: {live_result.get('skipped_count')}.",
        f"- [F] Failed sources: {live_result.get('failed_count')}.",
        "",
        "## 2.1 Source Parser Diagnostics",
        "",
        *_render_source_diagnostics(source_diagnostics),
        "",
        "## 3. Observed Items",
        "",
    ]
    changed_ids = _changed_item_ids(report_input)
    if changed_ids:
        for item_id in changed_ids:
            item = report_input.items_by_id[item_id]
            classification = report_input.classifications_by_id[item_id]
            score = report_input.scores_by_id.get(item_id)
            lines.extend(
                [
                    f"- [F] `{item_id}` - {item.title}",
                    f"  - [F] novelty: {_novelty(report_input, item_id)}.",
                    f"  - [F] source: {item.source_id}.",
                    f"  - [F] category: {classification.category}.",
                    f"  - [F] severity: {classification.severity}.",
                    f"  - [F] confidence: {item.confidence:.2f}.",
                    f"  - [F] score: {score.score if score is not None else 'n/a'}.",
                    f"  - [F] url: {item.url}",
                    f"  - [F] evidence: {item.evidence}",
                ]
            )
    else:
        lines.append("- [F] No new, changed or removed item.")
    lines.extend(["", "## 4. Project Impacts", ""])
    if report_input.project_impacts:
        for impact in report_input.project_impacts:
            lines.extend(
                [
                    f"- [F] {impact.project_name}: {impact.impact_level} for `{impact.item_id}`.",
                    f"  - [INT] reasons: {'; '.join(impact.reasons)}.",
                    f"  - [PROP] actions: {'; '.join(impact.suggested_actions)}.",
                ]
            )
    else:
        lines.append("- [F] No project impact detected.")
    lines.extend(
        [
            "",
            "## 5. Risks",
            "",
            "- [F] Live fetch is read-only and explicit.",
            "- [F] Runtime outputs are outside the repository.",
            "- [F] Unsupported sources are skipped rather than parsed heuristically.",
            "- [INT] First observation reports treat all parsed items as new when no previous snapshot is provided.",
            "",
            "## 6. Recommended Next Codex Step",
            "",
            "- [PROP] 0190) Review first real radar output and decide parser/source coverage hardening.",
        ]
    )
    return _join_lines(lines)


def _render_real_compact_report(
    report_input: ReportInput,
    live_result: dict[str, Any],
    report_status: str,
) -> str:
    lines = [
        f"# AI Release Radar Compact Real Report - {report_input.run_id}",
        "",
        f"- [F] status: {report_status}.",
        f"- [F] sources checked: {live_result.get('source_count')}.",
        f"- [F] parsed sources: {live_result.get('parsed_count')}.",
        f"- [F] items found: {len(report_input.items_by_id)}.",
        (
            "- [F] diff: "
            f"{len(report_input.diff_result.new_items)} new, "
            f"{len(report_input.diff_result.changed_items)} changed, "
            f"{len(report_input.diff_result.removed_items)} removed."
        ),
        "",
        "## Top Actions",
        "",
    ]
    if report_input.project_impacts:
        for impact in report_input.project_impacts[:5]:
            lines.append(
                f"- [PROP] {impact.project_name}: {impact.suggested_actions[0]} "
                f"for `{impact.item_id}` ({impact.impact_level})."
            )
    else:
        lines.append("- [PROP] No project action before manual review.")
    lines.append("- [PROP] 0190) Review first real radar output and source coverage.")
    return _join_lines(lines)


def _render_source_diagnostics(source_diagnostics: list[dict[str, Any]]) -> list[str]:
    if not source_diagnostics:
        return ["- [F] No source diagnostics available."]
    lines: list[str] = []
    for source in source_diagnostics:
        error = source.get("error")
        lines.append(
            "- [F] "
            f"`{source.get('source_id')}`; "
            f"type={source.get('source_type')}; "
            f"fetch_status={source.get('fetch_status')}; "
            f"http_status_code={source.get('http_status_code')}; "
            f"parser_status={source.get('parser_status')}; "
            f"item_count={source.get('item_count')}; "
            f"error={error if error is not None else 'none'}."
        )
    return lines


def _changed_item_ids(report_input: ReportInput) -> list[str]:
    return sorted(
        set(report_input.diff_result.new_items)
        | set(report_input.diff_result.changed_items)
        | set(report_input.diff_result.removed_items)
    )


def _novelty(report_input: ReportInput, item_id: str) -> str:
    if item_id in report_input.diff_result.new_items:
        return "new"
    if item_id in report_input.diff_result.changed_items:
        return "changed"
    if item_id in report_input.diff_result.removed_items:
        return "removed"
    return "unchanged"


def _outside_repo_output_dir(output_dir: str) -> Path:
    target_dir = Path(output_dir).expanduser().resolve()
    if _is_path_within(target_dir, REPO_ROOT):
        raise ValueError("real-run output_dir must be outside repository.")
    if target_dir.name.startswith("LAST-") or target_dir.name.startswith("latest-"):
        raise ValueError("real-run output_dir must not use LAST-* or latest-* names.")
    return target_dir


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _run_id_from_timestamp(timestamp: str) -> str:
    safe = timestamp.replace(":", "").replace("-", "").replace("T", "-")
    return f"0180-{safe}"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _join_lines(lines: list[str]) -> str:
    return "\n".join(lines).rstrip("\n") + "\n"

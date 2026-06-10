"""Locate and summarize AI Release Radar Bridge daily-sim runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from radar.run_index import (
    get_last_run_index_entry,
    validate_run_index,
)

from radar_web.bridge_reader import (
    FORBIDDEN_PREFIXES,
    load_daily_sim_summary,
    load_gate_report,
    load_hag_report,
    load_json,
    load_operator_dashboard,
    load_run_summary,
    load_text,
)


DAILY_SIM_DIR_PREFIX = "0320_0400_daily_sim_"


@dataclass(frozen=True)
class RunCandidate:
    """One Bridge daily-sim run discovered without modifying Bridge files."""

    run_id: str
    run_dir: str
    sort_key: str
    status: str = "NO_DATA"
    automation_gate_status: str = "NO_DATA"
    daily_quality_gate_status: str = "NO_DATA"
    source_coverage_status: str = "NO_DATA"
    scheduler_readiness: str = "NO_DATA"
    action_triage_status: str = "NO_DATA"
    hag_status: str = "NO_DATA"
    source_count: int | None = None
    parsed_count: int | None = None
    direct_action_count: int = 0
    monitor_only_action_count: int = 0
    blocked_action_count: int = 0
    manual_review_queue_count: int = 0
    prompt_suggestions_count: int = 0
    files: dict[str, str] = field(default_factory=dict)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "sort_key": self.sort_key,
            "status": self.status,
            "automation_gate_status": self.automation_gate_status,
            "daily_quality_gate_status": self.daily_quality_gate_status,
            "source_coverage_status": self.source_coverage_status,
            "scheduler_readiness": self.scheduler_readiness,
            "action_triage_status": self.action_triage_status,
            "hag_status": self.hag_status,
            "source_count": self.source_count,
            "parsed_count": self.parsed_count,
            "direct_action_count": self.direct_action_count,
            "monitor_only_action_count": self.monitor_only_action_count,
            "blocked_action_count": self.blocked_action_count,
            "manual_review_queue_count": self.manual_review_queue_count,
            "prompt_suggestions_count": self.prompt_suggestions_count,
            "files": dict(self.files),
            "warnings": list(self.warnings),
        }


def find_latest_run(runs_root: str | Path) -> RunCandidate | None:
    """Return the most recent coherent Bridge run, or None when no run exists."""
    runs = list_recent_runs(runs_root, limit=1)
    return runs[0] if runs else None


def inspect_runs_root(runs_root: str | Path) -> list[str]:
    """Return read-only data completeness warnings for the runs root."""
    root = Path(runs_root)
    warnings: list[str] = []
    if _has_forbidden_path_part(root):
        warnings.append(f"forbidden_path_name:{root.name}")
        return warnings
    if not root.exists():
        warnings.append("runs_root_missing")
        return warnings
    if not root.is_dir():
        warnings.append("runs_root_not_directory")
        return warnings
    index_path = root / "runs_index.jsonl"
    if index_path.exists() and not _has_forbidden_path_part(index_path):
        try:
            warnings.extend(f"runs_index:{issue}" for issue in validate_run_index(index_path))
            get_last_run_index_entry(index_path)
        except (OSError, ValueError) as exc:
            warnings.append(f"runs_index_unreadable:{exc}")
    return warnings


def list_recent_runs(runs_root: str | Path, limit: int = 20) -> list[RunCandidate]:
    """List recent daily-sim Bridge runs, preferring indexed/dated run directories."""
    if limit < 1:
        return []
    root = Path(runs_root)
    if _has_forbidden_path_part(root):
        return []
    run_dirs = _discover_run_dirs(root)
    candidates = [_candidate_from_dir(run_dir) for run_dir in run_dirs]
    candidates = sorted(candidates, key=lambda item: item.sort_key, reverse=True)
    return candidates[:limit]


def load_run_detail(runs_root: str | Path, run_id: str) -> dict[str, Any] | None:
    """Load a detailed read-only view for one run id."""
    run_dir = _resolve_run_dir(runs_root, run_id)
    if run_dir is None:
        return None
    candidate = _candidate_from_dir(run_dir)
    run_summary = load_run_summary(run_dir)
    daily_sim_summary = load_daily_sim_summary(run_dir)
    compact_report = load_text(run_dir / "0180-Report_Compact.md")
    gate_report = load_gate_report(run_dir)
    hag_report = load_hag_report(run_dir)
    operator_dashboard = load_operator_dashboard(run_dir)
    summary_data = _mapping(daily_sim_summary.data)
    real_run = _mapping(summary_data.get("real_run") or _mapping(run_summary.data).get("result"))
    action_triage = _mapping(
        summary_data.get("action_triage")
        or operator_dashboard.get("action_triage_json", {}).get("data")
    )
    prompt_suggestions = _mapping(
        summary_data.get("prompt_suggestions")
        or hag_report.get("prompt_suggestions_json", {}).get("data")
    )
    automation_gate = _mapping(summary_data.get("automation_gate"))
    source_diagnostics = _list(real_run.get("source_diagnostics"))
    triage_entries = _list(action_triage.get("entries"))
    detail = {
        "run": candidate.to_dict(),
        "run_summary": run_summary.to_dict(),
        "daily_sim_summary": daily_sim_summary.to_dict(),
        "compact_report": compact_report.to_dict(),
        "gate_report": gate_report,
        "hag_report": hag_report,
        "operator_dashboard": operator_dashboard,
        "source_diagnostics": source_diagnostics,
        "source_diagnostics_summary": _source_diagnostics_summary(source_diagnostics),
        "direct_actions": [
            entry
            for entry in triage_entries
            if _mapping(entry).get("triage_class") == "codex_prompt_candidate"
        ],
        "blocked_actions": [
            entry
            for entry in triage_entries
            if _mapping(entry).get("triage_class")
            in {"blocked_by_coverage", "blocked_by_manual_review"}
        ],
        "monitor_only_summary": [
            entry for entry in triage_entries if _mapping(entry).get("triage_class") == "monitor"
        ],
        "manual_review_queue": _manual_review_queue(automation_gate, summary_data, triage_entries),
        "prompt_suggestions": _list(prompt_suggestions.get("suggestions")),
        "prompt_suggestions_status": prompt_suggestions.get("status", "NO_DATA"),
        "no_auto_action": True,
        "warnings": _detail_warnings(
            run_summary,
            daily_sim_summary,
            compact_report,
            gate_report,
            hag_report,
            operator_dashboard,
            candidate,
        ),
    }
    return detail


def _discover_run_dirs(root: Path) -> list[Path]:
    discovered: dict[str, Path] = {}
    root_index = root / "runs_index.jsonl"
    if root_index.exists() and not _has_forbidden_path_part(root_index):
        try:
            entry = get_last_run_index_entry(root_index)
            if entry is not None:
                candidate = Path(entry.snapshot_dir)
                if candidate.is_dir() and not _has_forbidden_path_part(candidate):
                    discovered[str(candidate.resolve()).lower()] = candidate
        except (OSError, ValueError):
            pass
    if root.exists():
        for child in root.iterdir():
            if child.is_dir() and child.name.startswith(DAILY_SIM_DIR_PREFIX):
                if not _has_forbidden_path_part(child):
                    discovered[str(child.resolve()).lower()] = child
    return list(discovered.values())


def _candidate_from_dir(run_dir: Path) -> RunCandidate:
    warnings: list[str] = []
    daily_summary = load_daily_sim_summary(run_dir)
    run_summary = load_run_summary(run_dir)
    warnings.extend(daily_summary.warnings)
    warnings.extend(run_summary.warnings)
    summary_data = _mapping(daily_summary.data)
    run_summary_data = _mapping(run_summary.data)
    real_run = _mapping(summary_data.get("real_run") or run_summary_data.get("result"))
    automation_gate = _mapping(summary_data.get("automation_gate"))
    daily_quality = _mapping(summary_data.get("daily_quality_gate_v2"))
    action_triage = _mapping(summary_data.get("action_triage"))
    prompt_suggestions = _mapping(summary_data.get("prompt_suggestions"))
    triage_counts = _mapping(action_triage.get("counts"))
    index_path = run_dir / "runs_index.jsonl"
    if index_path.exists():
        try:
            warnings.extend(f"runs_index:{issue}" for issue in validate_run_index(index_path))
            index_entry = get_last_run_index_entry(index_path)
            if index_entry is not None and "report_compact" not in real_run:
                real_run["report_compact"] = index_entry.report_compact
        except (OSError, ValueError) as exc:
            warnings.append(f"runs_index_error:{exc}")
    files = _existing_files(run_dir, summary_data, real_run)
    return RunCandidate(
        run_id=run_dir.name,
        run_dir=str(run_dir),
        sort_key=_sort_key(run_dir),
        status=_string(summary_data.get("status") or real_run.get("status")),
        automation_gate_status=_string(
            summary_data.get("automation_gate_status") or automation_gate.get("status")
        ),
        daily_quality_gate_status=_string(daily_quality.get("overall_daily_review_status")),
        source_coverage_status=_string(daily_quality.get("source_coverage_status")),
        scheduler_readiness=_string(summary_data.get("scheduler_readiness_recommendation")),
        action_triage_status=_string(
            summary_data.get("action_triage_status") or action_triage.get("status")
        ),
        hag_status=_string(summary_data.get("hag_status")),
        source_count=_int_or_none(real_run.get("source_count")),
        parsed_count=_int_or_none(real_run.get("parsed_count")),
        direct_action_count=_int(real_run.get("direct_action_count")),
        monitor_only_action_count=_int(real_run.get("monitor_only_action_count")),
        blocked_action_count=(
            _int(triage_counts.get("blocked_by_coverage"))
            + _int(triage_counts.get("blocked_by_manual_review"))
        ),
        manual_review_queue_count=_int(summary_data.get("manual_review_queue_count")),
        prompt_suggestions_count=_int(
            summary_data.get("prompt_suggestions_count")
            or prompt_suggestions.get("suggestions_count")
        ),
        files=files,
        warnings=tuple(sorted(set(warnings))),
    )


def _existing_files(
    run_dir: Path,
    summary_data: dict[str, Any],
    real_run: dict[str, Any],
) -> dict[str, str]:
    declared = {
        "report_compact": real_run.get("report_compact"),
        "run_summary": real_run.get("run_summary"),
        "daily_sim_summary": summary_data.get("daily_sim_summary"),
        "automation_gate_markdown": summary_data.get("automation_gate_markdown"),
        "daily_quality_gate_v2_markdown": summary_data.get("daily_quality_gate_v2_markdown"),
        "action_triage_json": summary_data.get("action_triage_json"),
        "prompt_suggestions_markdown": summary_data.get("prompt_suggestions_markdown"),
        "hag_report_markdown": summary_data.get("hag_report_markdown"),
        "dashboard_path": summary_data.get("dashboard_path"),
        "supervised_action_loop_dry_run": summary_data.get("supervised_action_loop_dry_run"),
    }
    fallback = {
        "report_compact": run_dir / "0180-Report_Compact.md",
        "run_summary": run_dir / "0180-Run_Summary.json",
        "daily_sim_summary": run_dir / "0350-Daily_Sim_Summary.json",
        "automation_gate_markdown": run_dir / "0350-Daily_Sim_Gate.md",
        "daily_quality_gate_v2_markdown": run_dir / "0630-Daily_Quality_Gate_V2.md",
        "action_triage_json": run_dir / "0650-Action_Triage.json",
        "prompt_suggestions_markdown": run_dir / "0660-Codex_Prompt_Suggestions.md",
        "hag_report_markdown": run_dir / "0680-Human_Approval_Gate_Report.md",
        "dashboard_path": run_dir / "0710-Daily_Operator_Dashboard.md",
        "supervised_action_loop_dry_run": run_dir / "0730-Supervised_Action_Loop_Dry_Run.md",
    }
    files: dict[str, str] = {}
    for key, raw in declared.items():
        candidate = Path(raw) if isinstance(raw, str) and raw.strip() else fallback[key]
        if candidate.exists() and not _has_forbidden_path_part(candidate):
            files[key] = str(candidate)
    return files


def _resolve_run_dir(runs_root: str | Path, run_id: str) -> Path | None:
    if not run_id or run_id.startswith(FORBIDDEN_PREFIXES) or any(part in run_id for part in ("/", "\\")):
        return None
    root = Path(runs_root)
    direct = root / run_id
    if direct.is_dir() and not _has_forbidden_path_part(direct):
        return direct
    for candidate in list_recent_runs(root):
        if candidate.run_id == run_id:
            return Path(candidate.run_dir)
    return None


def _sort_key(run_dir: Path) -> str:
    stamp = run_dir.name.removeprefix(DAILY_SIM_DIR_PREFIX)
    try:
        parsed = datetime.strptime(stamp, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
        return parsed.isoformat()
    except ValueError:
        try:
            return datetime.fromtimestamp(run_dir.stat().st_mtime, tz=timezone.utc).isoformat()
        except OSError:
            return "0001-01-01T00:00:00+00:00"


def _source_diagnostics_summary(source_diagnostics: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for raw in source_diagnostics:
        source = _mapping(raw)
        status = str(source.get("diagnostic_status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _manual_review_queue(
    automation_gate: dict[str, Any],
    summary_data: dict[str, Any],
    triage_entries: list[Any],
) -> list[Any]:
    queue = _list(summary_data.get("manual_review_queue") or automation_gate.get("manual_review_queue"))
    if queue:
        return queue
    return [
        entry
        for entry in triage_entries
        if _mapping(entry).get("triage_class") == "manual_review"
    ]


def _detail_warnings(
    *items: Any,
) -> list[str]:
    warnings: list[str] = []
    for item in items:
        if hasattr(item, "warnings"):
            warnings.extend(getattr(item, "warnings"))
        elif isinstance(item, dict):
            warnings.extend(str(warning) for warning in item.get("warnings", []))
    return sorted(set(warnings))


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any) -> str:
    return value if isinstance(value, str) and value.strip() else "NO_DATA"


def _int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _has_forbidden_path_part(path: Path) -> bool:
    return any(part.startswith(FORBIDDEN_PREFIXES) for part in path.parts)

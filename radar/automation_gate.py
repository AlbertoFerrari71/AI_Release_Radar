"""Deterministic automation-readiness gate for real-run outputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from radar.json_utils import read_json
from radar.manual_review_queue import build_manual_review_queue
from radar.run_index import validate_run_index


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_SUMMARY_FILENAME = "0180-Run_Summary.json"
REPORT_FULL_FILENAME = "0180-Report_Full.md"
REPORT_COMPACT_FILENAME = "0180-Report_Compact.md"
RUN_INDEX_ENTRY_FILENAME = "0180-Run_Index_Entry.json"
RUNS_INDEX_FILENAME = "runs_index.jsonl"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
ACTION_REVIEW_REQUIRED = "ACTION_REVIEW_REQUIRED"
FAIL = "FAIL"
SCHEDULER_GO = "GO"
SCHEDULER_GO_WITH_WARNINGS = "GO_WITH_WARNINGS"
SCHEDULER_HOLD = "HOLD"
SCHEDULER_STOP = "STOP"
ALLOWED_ZERO_ITEM_STATUSES = {"NO_CHANGE", "NO_PARSED_ITEMS"}
FULL_PASS_MIN_PARSED_RATIO = 0.50
SCHEDULER_HOLD_MAX_LOW_PARSED_RATIO = 0.25
HIGH_UNSUPPORTED_RATIO = 0.50
HIGH_MONITOR_ONLY_RATIO = 0.75


@dataclass(frozen=True)
class AutomationGateResult:
    """Serializable automation gate evaluation."""

    status: str
    recommendation: str
    output_dir: str
    summary_path: str | None
    metrics: dict[str, object]
    failures: list[str]
    warnings: list[str]
    required_outputs: dict[str, str]
    scheduler_readiness_recommendation: str
    manual_review_queue: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "status": self.status,
            "recommendation": self.recommendation,
            "scheduler_readiness_recommendation": self.scheduler_readiness_recommendation,
            "output_dir": self.output_dir,
            "summary_path": self.summary_path,
            "metrics": dict(self.metrics),
            "failures": list(self.failures),
            "warnings": list(self.warnings),
            "required_outputs": dict(self.required_outputs),
            "manual_review_queue": [dict(entry) for entry in self.manual_review_queue],
        }


def evaluate_automation_gate(
    output_dir: str | Path,
    *,
    repo_root: str | Path = REPO_ROOT,
) -> AutomationGateResult:
    """Evaluate whether a real-run output directory is automation-ready."""
    target_dir = Path(output_dir).expanduser().resolve()
    root = Path(repo_root).expanduser().resolve()
    failures: list[str] = []
    warnings: list[str] = []
    required_outputs: dict[str, str] = {}
    metrics = _empty_metrics()

    if _is_path_within(target_dir, root):
        failures.append("output_dir_inside_repository")
    if _has_forbidden_path_part(target_dir):
        failures.append("output_dir_uses_forbidden_last_or_latest_name")

    summary_path = target_dir / RUN_SUMMARY_FILENAME
    if not summary_path.is_file():
        failures.append("run_summary_missing")
        return _build_result(target_dir, summary_path, metrics, failures, warnings, required_outputs)

    try:
        summary_data = read_json(summary_path)
    except (OSError, ValueError) as exc:
        failures.append(f"run_summary_invalid: {exc}")
        return _build_result(target_dir, summary_path, metrics, failures, warnings, required_outputs)

    result = _summary_result(summary_data)
    if result is None:
        failures.append("run_summary_result_missing")
        return _build_result(target_dir, summary_path, metrics, failures, warnings, required_outputs)

    source_diagnostics = _source_diagnostics(summary_data, result)
    metrics = _metrics_from_result(result, source_diagnostics, failures, warnings)
    required_outputs = _required_outputs(target_dir, result)
    _check_required_outputs(required_outputs, failures)
    _check_run_index(required_outputs.get("runs_index"), failures)
    _check_metric_rules(metrics, failures, warnings)
    manual_review_queue = build_manual_review_queue(
        result=result,
        source_diagnostics=source_diagnostics,
        metrics=metrics,
    )
    metrics["manual_review_queue_count"] = len(manual_review_queue)

    return _build_result(
        target_dir,
        summary_path,
        metrics,
        failures,
        warnings,
        required_outputs,
        manual_review_queue,
    )


def render_automation_gate_markdown(gate: AutomationGateResult) -> str:
    """Render a deterministic Markdown gate report."""
    metrics = gate.metrics
    lines = [
        "# 0350) Daily Simulation Automation Gate",
        "",
        f"- [F] automation_gate_status: {gate.status}.",
        f"- [F] recommendation: {gate.recommendation}",
        (
            "- [F] scheduler_readiness_recommendation: "
            f"{gate.scheduler_readiness_recommendation}"
        ),
        f"- [F] output_dir: {gate.output_dir}",
        f"- [F] run_summary: {gate.summary_path or 'missing'}",
        "",
        "## Metrics",
        "",
    ]
    for key in sorted(metrics):
        lines.append(f"- [F] {key}: {metrics[key]}")
    lines.extend(["", "## Failures", ""])
    if gate.failures:
        lines.extend(f"- [F] {failure}" for failure in gate.failures)
    else:
        lines.append("- [F] none")
    lines.extend(["", "## Warnings", ""])
    if gate.warnings:
        lines.extend(f"- [F] {warning}" for warning in gate.warnings)
    else:
        lines.append("- [F] none")
    lines.extend(["", "## Manual Review Queue", ""])
    if gate.manual_review_queue:
        for entry in gate.manual_review_queue:
            lines.append(
                "- [F] "
                f"type={entry.get('type')}; "
                f"source_id={entry.get('source_id')}; "
                f"reason={entry.get('reason')}; "
                f"severity={entry.get('severity')}; "
                f"blocking_for_scheduler={entry.get('blocking_for_scheduler')}; "
                f"recommended_follow_up={entry.get('recommended_follow_up')}."
            )
    else:
        lines.append("- [F] none")
    return "\n".join(lines).rstrip("\n") + "\n"


def _build_result(
    target_dir: Path,
    summary_path: Path,
    metrics: dict[str, object],
    failures: list[str],
    warnings: list[str],
    required_outputs: dict[str, str],
    manual_review_queue: list[dict[str, object]] | None = None,
) -> AutomationGateResult:
    status = _status_from_findings(metrics, failures, warnings)
    return AutomationGateResult(
        status=status,
        recommendation=_recommendation(status),
        output_dir=str(target_dir),
        summary_path=str(summary_path) if summary_path.exists() else None,
        metrics=metrics,
        failures=failures,
        warnings=warnings,
        required_outputs=required_outputs,
        scheduler_readiness_recommendation=_scheduler_readiness_recommendation(
            metrics,
            failures,
            warnings,
        ),
        manual_review_queue=list(manual_review_queue or []),
    )


def _status_from_findings(
    metrics: dict[str, object],
    failures: list[str],
    warnings: list[str],
) -> str:
    if failures:
        return FAIL
    if _metric_int(metrics, "direct_action_count") > 0:
        return ACTION_REVIEW_REQUIRED
    if warnings:
        return PASS_WITH_WARNINGS
    return PASS


def _recommendation(status: str) -> str:
    if status == FAIL:
        return "Fix failed gate conditions before any scheduler or unattended run."
    if status == ACTION_REVIEW_REQUIRED:
        return "Manual review required before acting on direct actions; no auto-action."
    if status == PASS_WITH_WARNINGS:
        return "Controlled daily simulation can continue, but scheduler readiness remains held."
    return "No gate blockers detected; keep human approval before scheduler activation."


def _scheduler_readiness_recommendation(
    metrics: dict[str, object],
    failures: list[str],
    warnings: list[str],
) -> str:
    if failures:
        return SCHEDULER_STOP
    source_count = _metric_int(metrics, "source_count")
    unsupported_count = _metric_int(metrics, "unsupported_source_count")
    parsed_ratio = float(metrics.get("parsed_ratio") or 0.0)
    if _metric_int(metrics, "parsed_count") == 0:
        return SCHEDULER_STOP
    if parsed_ratio < SCHEDULER_HOLD_MAX_LOW_PARSED_RATIO:
        return SCHEDULER_HOLD
    if _metric_int(metrics, "direct_action_count") > 0:
        return SCHEDULER_HOLD
    if _metric_int(metrics, "manual_review_required_count") > 0:
        return SCHEDULER_HOLD
    if source_count and unsupported_count / source_count >= HIGH_UNSUPPORTED_RATIO:
        return SCHEDULER_HOLD
    if warnings:
        return SCHEDULER_GO_WITH_WARNINGS
    return SCHEDULER_GO


def _summary_result(summary_data: object) -> dict[str, Any] | None:
    if not isinstance(summary_data, dict):
        return None
    result = summary_data.get("result")
    return result if isinstance(result, dict) else None


def _source_diagnostics(
    summary_data: dict[str, Any],
    result: dict[str, Any],
) -> list[dict[str, Any]]:
    diagnostics = summary_data.get("source_diagnostics")
    if not isinstance(diagnostics, list):
        diagnostics = result.get("source_diagnostics")
    if not isinstance(diagnostics, list):
        return []
    return [entry for entry in diagnostics if isinstance(entry, dict)]


def _metrics_from_result(
    result: dict[str, Any],
    source_diagnostics: list[dict[str, Any]],
    failures: list[str],
    warnings: list[str],
) -> dict[str, object]:
    metrics = {
        "run_id": result.get("run_id"),
        "status": result.get("status"),
        "source_count": _required_int(result, "source_count", failures),
        "parsed_count": _required_int(result, "parsed_count", failures),
        "item_count": _required_int(result, "item_count", failures),
        "failed_count": _required_int(result, "failed_count", failures),
        "skipped_count": _required_int(result, "skipped_count", failures),
        "unsupported_source_count": _optional_int(
            result,
            "unsupported_source_count",
            _count_diagnostics(source_diagnostics, "fetched_but_unsupported"),
        ),
        "manual_review_required_count": _optional_int(
            result,
            "manual_review_required_count",
            _manual_review_required_count(source_diagnostics),
        ),
        "direct_action_count": _required_int(result, "direct_action_count", failures),
        "monitor_only_action_count": _required_int(
            result,
            "monitor_only_action_count",
            failures,
        ),
        "no_action_count": _required_int(result, "no_action_count", failures),
        "report_scorecard_status": _report_scorecard_status(result),
        "source_diagnostic_count": len(source_diagnostics),
    }
    if not source_diagnostics:
        warnings.append("source_diagnostics_missing")
    source_count = _metric_int(metrics, "source_count")
    parsed_count = _metric_int(metrics, "parsed_count")
    metrics["parsed_ratio"] = round(parsed_count / source_count, 4) if source_count else 0.0
    return metrics


def _required_int(
    result: dict[str, Any],
    key: str,
    failures: list[str],
) -> int:
    value = result.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        failures.append(f"{key}_missing_or_not_integer")
        return 0
    return value


def _optional_int(result: dict[str, Any], key: str, default: int) -> int:
    value = result.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return value


def _report_scorecard_status(result: dict[str, Any]) -> str | None:
    value = result.get("report_scorecard_status")
    return value if isinstance(value, str) else None


def _count_diagnostics(source_diagnostics: list[dict[str, Any]], status: str) -> int:
    return sum(1 for source in source_diagnostics if source.get("diagnostic_status") == status)


def _manual_review_required_count(source_diagnostics: list[dict[str, Any]]) -> int:
    return sum(
        1
        for source in source_diagnostics
        if source.get("diagnostic_status") == "manual_review_required"
        or source.get("manual_review_required") is True
    )


def _required_outputs(target_dir: Path, result: dict[str, Any]) -> dict[str, str]:
    return {
        "report_full": _output_path(result, "report_full", target_dir / REPORT_FULL_FILENAME),
        "report_compact": _output_path(
            result,
            "report_compact",
            target_dir / REPORT_COMPACT_FILENAME,
        ),
        "run_summary": _output_path(result, "run_summary", target_dir / RUN_SUMMARY_FILENAME),
        "run_index_entry": _output_path(
            result,
            "run_index_entry",
            target_dir / RUN_INDEX_ENTRY_FILENAME,
        ),
        "runs_index": _output_path(result, "runs_index", target_dir / RUNS_INDEX_FILENAME),
    }


def _output_path(result: dict[str, Any], key: str, fallback: Path) -> str:
    value = result.get(key)
    if isinstance(value, str) and value.strip():
        return str(Path(value).expanduser().resolve())
    return str(fallback.resolve())


def _check_required_outputs(required_outputs: dict[str, str], failures: list[str]) -> None:
    for key, raw_path in required_outputs.items():
        path = Path(raw_path)
        if _has_forbidden_path_part(path):
            failures.append(f"{key}_uses_forbidden_last_or_latest_name")
        if not path.is_file():
            failures.append(f"{key}_missing")


def _check_run_index(raw_path: str | None, failures: list[str]) -> None:
    if raw_path is None or not Path(raw_path).is_file():
        return
    try:
        issues = validate_run_index(raw_path)
    except (OSError, ValueError) as exc:
        failures.append(f"runs_index_invalid: {exc}")
        return
    for issue in issues:
        failures.append(f"runs_index_invalid: {issue}")


def _check_metric_rules(
    metrics: dict[str, object],
    failures: list[str],
    warnings: list[str],
) -> None:
    source_count = _metric_int(metrics, "source_count")
    parsed_count = _metric_int(metrics, "parsed_count")
    item_count = _metric_int(metrics, "item_count")
    failed_count = _metric_int(metrics, "failed_count")
    unsupported_count = _metric_int(metrics, "unsupported_source_count")
    manual_count = _metric_int(metrics, "manual_review_required_count")
    direct_count = _metric_int(metrics, "direct_action_count")
    monitor_count = _metric_int(metrics, "monitor_only_action_count")
    no_action_count = _metric_int(metrics, "no_action_count")
    status = metrics.get("status")
    parsed_ratio = float(metrics.get("parsed_ratio") or 0.0)

    if source_count == 0:
        failures.append("source_count_zero")
    if parsed_count == 0:
        failures.append("parsed_count_zero")
    if item_count == 0 and status not in ALLOWED_ZERO_ITEM_STATUSES:
        failures.append("item_count_zero_without_no_change_status")
    if parsed_ratio < FULL_PASS_MIN_PARSED_RATIO:
        warnings.append(
            f"low_source_coverage: parsed_count/source_count={parsed_count}/{source_count}"
        )
    if failed_count > 0:
        warnings.append(f"fetch_failures_present: failed_count={failed_count}")
    if manual_count > 0:
        warnings.append(f"manual_review_required_present: count={manual_count}")
    if source_count and unsupported_count / source_count >= HIGH_UNSUPPORTED_RATIO:
        warnings.append(f"unsupported_source_count_high: {unsupported_count}/{source_count}")
    total_actions = direct_count + monitor_count + no_action_count
    if total_actions and monitor_count / total_actions >= HIGH_MONITOR_ONLY_RATIO:
        warnings.append(f"monitor_only_volume_high: {monitor_count}/{total_actions}")
    if metrics.get("report_scorecard_status") != "PASS":
        warnings.append(
            f"report_scorecard_not_pass: {metrics.get('report_scorecard_status')}"
        )


def _metric_int(metrics: dict[str, object], key: str) -> int:
    value = metrics.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value


def _empty_metrics() -> dict[str, object]:
    return {
        "run_id": None,
        "status": None,
        "source_count": 0,
        "parsed_count": 0,
        "item_count": 0,
        "failed_count": 0,
        "skipped_count": 0,
        "unsupported_source_count": 0,
        "manual_review_required_count": 0,
        "direct_action_count": 0,
        "monitor_only_action_count": 0,
        "no_action_count": 0,
        "report_scorecard_status": None,
        "source_diagnostic_count": 0,
        "parsed_ratio": 0.0,
        "manual_review_queue_count": 0,
    }


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _has_forbidden_path_part(path: Path) -> bool:
    return any(part.startswith("LAST-") or part.startswith("latest-") for part in path.parts)

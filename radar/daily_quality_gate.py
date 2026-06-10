"""Daily report quality gate v2 with separate review dimensions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PASS = "PASS"
WARN = "WARN"
HOLD = "HOLD"
ACTION_REVIEW_REQUIRED = "ACTION_REVIEW_REQUIRED"
FAIL = "FAIL"
QUALITY_STATUSES = (PASS, WARN, HOLD, ACTION_REVIEW_REQUIRED, FAIL)
OVERALL_PRIORITY = {
    PASS: 0,
    WARN: 1,
    HOLD: 2,
    ACTION_REVIEW_REQUIRED: 3,
    FAIL: 4,
}


@dataclass(frozen=True)
class DailyQualityGateResult:
    """Serializable daily quality gate v2 result."""

    report_readability_status: str
    source_coverage_status: str
    actionability_status: str
    overall_daily_review_status: str
    warnings: list[str]
    metrics: dict[str, object]

    def __post_init__(self) -> None:
        for field_name in (
            "report_readability_status",
            "source_coverage_status",
            "actionability_status",
            "overall_daily_review_status",
        ):
            value = getattr(self, field_name)
            if value not in QUALITY_STATUSES:
                raise ValueError(f"unsupported {field_name}: {value}")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "report_readability_status": self.report_readability_status,
            "source_coverage_status": self.source_coverage_status,
            "actionability_status": self.actionability_status,
            "overall_daily_review_status": self.overall_daily_review_status,
            "warnings": list(self.warnings),
            "metrics": dict(self.metrics),
        }


def evaluate_daily_quality_gate(data: object) -> DailyQualityGateResult:
    """Evaluate daily review quality from an automation gate or daily summary."""
    gate = _gate_dict(data)
    metrics = _metrics(gate, data)
    gate_status = _str(gate.get("status")) or _str(_mapping(data).get("automation_gate_status"))
    gate_warnings = _str_list(gate.get("warnings"))
    gate_failures = _str_list(gate.get("failures"))
    manual_review_queue = _list(gate.get("manual_review_queue"))

    warnings: list[str] = []
    report_readability_status = _report_readability_status(metrics, warnings)
    source_coverage_status = _source_coverage_status(metrics, gate_warnings, gate_failures, warnings)
    actionability_status = _actionability_status(
        metrics,
        gate_status,
        gate_failures,
        gate_warnings,
        manual_review_queue,
        warnings,
    )
    overall = _overall_status(
        report_readability_status,
        source_coverage_status,
        actionability_status,
    )
    return DailyQualityGateResult(
        report_readability_status=report_readability_status,
        source_coverage_status=source_coverage_status,
        actionability_status=actionability_status,
        overall_daily_review_status=overall,
        warnings=sorted(set(warnings)),
        metrics=metrics,
    )


def render_daily_quality_gate_markdown(result: DailyQualityGateResult) -> str:
    """Render the daily quality gate as deterministic Markdown."""
    lines = [
        "# 0630) Daily Report Quality Gate v2",
        "",
        f"- [F] report_readability_status: {result.report_readability_status}.",
        f"- [F] source_coverage_status: {result.source_coverage_status}.",
        f"- [F] actionability_status: {result.actionability_status}.",
        f"- [F] overall_daily_review_status: {result.overall_daily_review_status}.",
        "",
        "## Metrics",
        "",
    ]
    for key in sorted(result.metrics):
        lines.append(f"- [F] {key}: {result.metrics[key]}")
    lines.extend(["", "## Warnings", ""])
    if result.warnings:
        lines.extend(f"- [F] {warning}" for warning in result.warnings)
    else:
        lines.append("- [F] none")
    return "\n".join(lines).rstrip("\n") + "\n"


def _gate_dict(data: object) -> dict[str, Any]:
    if hasattr(data, "to_dict") and callable(getattr(data, "to_dict")):
        data = data.to_dict()
    raw = _mapping(data)
    gate = raw.get("automation_gate")
    if isinstance(gate, dict):
        return gate
    return raw


def _metrics(gate: dict[str, Any], data: object) -> dict[str, object]:
    raw_metrics = _mapping(gate.get("metrics"))
    raw = _mapping(data)
    result = _mapping(raw.get("real_run") or raw.get("result"))
    metrics = {
        "source_count": _int_value(raw_metrics.get("source_count", result.get("source_count"))),
        "parsed_count": _int_value(raw_metrics.get("parsed_count", result.get("parsed_count"))),
        "item_count": _int_value(raw_metrics.get("item_count", result.get("item_count"))),
        "direct_action_count": _int_value(
            raw_metrics.get("direct_action_count", result.get("direct_action_count"))
        ),
        "monitor_only_action_count": _int_value(
            raw_metrics.get("monitor_only_action_count", result.get("monitor_only_action_count"))
        ),
        "manual_review_queue_count": _int_value(
            raw_metrics.get("manual_review_queue_count", raw.get("manual_review_queue_count"))
        ),
        "manual_review_required_count": _int_value(
            raw_metrics.get(
                "manual_review_required_count",
                result.get("manual_review_required_count"),
            )
        ),
        "unsupported_source_count": _int_value(
            raw_metrics.get("unsupported_source_count", result.get("unsupported_source_count"))
        ),
        "failed_count": _int_value(raw_metrics.get("failed_count", result.get("failed_count"))),
        "report_scorecard_status": _str(
            raw_metrics.get(
                "report_scorecard_status",
                result.get("report_scorecard_status"),
            )
        ),
    }
    source_count = int(metrics["source_count"])
    parsed_count = int(metrics["parsed_count"])
    metrics["parsed_ratio"] = round(parsed_count / source_count, 4) if source_count else 0.0
    return metrics


def _report_readability_status(metrics: dict[str, object], warnings: list[str]) -> str:
    scorecard = metrics.get("report_scorecard_status")
    if scorecard == PASS:
        return PASS
    if scorecard == FAIL:
        warnings.append("report_scorecard_failed")
        return FAIL
    warnings.append(f"report_scorecard_not_pass: {scorecard}")
    return WARN


def _source_coverage_status(
    metrics: dict[str, object],
    gate_warnings: list[str],
    gate_failures: list[str],
    warnings: list[str],
) -> str:
    source_count = _metric_int(metrics, "source_count")
    parsed_count = _metric_int(metrics, "parsed_count")
    parsed_ratio = float(metrics.get("parsed_ratio") or 0.0)
    if source_count == 0 or "source_count_zero" in gate_failures:
        warnings.append("source_count_zero")
        return FAIL
    if parsed_count == 0 or "parsed_count_zero" in gate_failures:
        warnings.append("parsed_count_zero")
        return FAIL
    if parsed_ratio < 0.50:
        warnings.append(f"low_source_coverage: parsed_count/source_count={parsed_count}/{source_count}")
        return WARN
    if _metric_int(metrics, "unsupported_source_count") > 0:
        warnings.append("unsupported_sources_present")
        return WARN
    if any(warning.startswith("low_source_coverage") for warning in gate_warnings):
        warnings.append("low_source_coverage")
        return WARN
    return PASS


def _actionability_status(
    metrics: dict[str, object],
    gate_status: str | None,
    gate_failures: list[str],
    gate_warnings: list[str],
    manual_review_queue: list[object],
    warnings: list[str],
) -> str:
    if gate_status == FAIL or gate_failures:
        warnings.append("automation_gate_failed")
        return FAIL
    if _metric_int(metrics, "direct_action_count") > 0 or gate_status == ACTION_REVIEW_REQUIRED:
        warnings.append("direct_actions_require_human_approval")
        return ACTION_REVIEW_REQUIRED
    if manual_review_queue or _metric_int(metrics, "manual_review_queue_count") > 0:
        warnings.append("manual_review_queue_present")
        return HOLD
    if _metric_int(metrics, "manual_review_required_count") > 0:
        warnings.append("manual_review_required_present")
        return HOLD
    if gate_warnings:
        warnings.append("automation_gate_warnings_present")
        return WARN
    return PASS


def _overall_status(*statuses: str) -> str:
    return max(statuses, key=lambda status: OVERALL_PRIORITY[status])


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _int_value(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value


def _metric_int(metrics: dict[str, object], key: str) -> int:
    return _int_value(metrics.get(key))


def _str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None

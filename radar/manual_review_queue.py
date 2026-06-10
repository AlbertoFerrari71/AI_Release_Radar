"""Deterministic manual review queue helpers for automation gate outputs."""

from __future__ import annotations

from typing import Any


SOURCE_QUEUE_STATUSES = {
    "fetch_failed",
    "fetched_but_empty",
    "fetched_but_truncated",
    "fetched_but_unsupported",
    "manual_review_required",
    "parser_failed",
}
HIGH_SEVERITY_SOURCE_STATUSES = {
    "fetch_failed",
    "manual_review_required",
    "parser_failed",
}
HIGH_COVERAGE_PRIORITIES = {"P0", "P1"}
COMBINED_RUN_SOURCE_ID = "0180_real_radar_run"


def build_manual_review_queue(
    *,
    result: dict[str, Any],
    source_diagnostics: list[dict[str, Any]],
    metrics: dict[str, object],
) -> list[dict[str, object]]:
    """Build a deterministic queue of sources/actions requiring manual review."""
    queue = [
        entry
        for source in source_diagnostics
        for entry in [_source_queue_entry(source)]
        if entry is not None
    ]
    direct_count = _metric_int(metrics, "direct_action_count")
    if direct_count > 0:
        queue.append(
            {
                "type": "action",
                "source_id": COMBINED_RUN_SOURCE_ID,
                "reason": "direct_actions_present",
                "severity": "high",
                "recommended_follow_up": "manual_review_direct_actions",
                "blocking_for_scheduler": True,
                "count": direct_count,
            }
        )
    if _metric_int(metrics, "parsed_count") == 0 and _metric_int(metrics, "source_count") > 0:
        queue.append(
            {
                "type": "source",
                "source_id": COMBINED_RUN_SOURCE_ID,
                "reason": "parsed_count_zero",
                "severity": "critical",
                "recommended_follow_up": "fix_parser_or_source_before_scheduler",
                "blocking_for_scheduler": True,
                "count": int(result.get("source_count", 0))
                if isinstance(result.get("source_count"), int)
                else _metric_int(metrics, "source_count"),
            }
        )
    return sorted(queue, key=_queue_sort_key)


def _source_queue_entry(source: dict[str, Any]) -> dict[str, object] | None:
    status = str(source.get("diagnostic_status") or "")
    if status not in SOURCE_QUEUE_STATUSES:
        return None
    coverage_priority = str(source.get("coverage_priority") or "")
    severity = _source_severity(status, coverage_priority)
    return {
        "type": "source",
        "source_id": str(source.get("source_id") or "unknown_source"),
        "reason": status,
        "severity": severity,
        "recommended_follow_up": _recommended_follow_up(source),
        "blocking_for_scheduler": _blocking_for_scheduler(source, severity),
    }


def _source_severity(status: str, coverage_priority: str) -> str:
    if status in HIGH_SEVERITY_SOURCE_STATUSES:
        return "high"
    if coverage_priority in HIGH_COVERAGE_PRIORITIES:
        return "high"
    return "medium"


def _recommended_follow_up(source: dict[str, Any]) -> str:
    for key in ("registry_recommended_follow_up", "recommended_follow_up"):
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "manual_review_source"


def _blocking_for_scheduler(source: dict[str, Any], severity: str) -> bool:
    scheduler_readiness = source.get("scheduler_readiness")
    return severity in {"critical", "high"} or scheduler_readiness in {"hold", "warn"}


def _metric_int(metrics: dict[str, object], key: str) -> int:
    value = metrics.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value


def _queue_sort_key(entry: dict[str, object]) -> tuple[int, str, str]:
    type_order = {"source": 0, "item": 1, "action": 2}
    return (
        type_order.get(str(entry.get("type")), 99),
        str(entry.get("source_id") or ""),
        str(entry.get("reason") or ""),
    )

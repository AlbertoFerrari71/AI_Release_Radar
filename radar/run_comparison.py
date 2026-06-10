"""Offline comparison helpers for manual radar run summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


NUMERIC_METRICS = (
    "sources_checked",
    "parsed_sources",
    "items",
    "project_impacts",
    "direct_actions",
    "monitor_only_actions",
    "failed_sources",
    "unsupported_sources",
)
STRING_METRICS = ("scorecard_result",)


@dataclass(frozen=True)
class MetricComparison:
    """One before/after metric comparison."""

    metric: str
    before: int | str | None
    after: int | str | None
    delta: int | None

    def to_dict(self) -> dict[str, object]:
        return {
            "metric": self.metric,
            "before": self.before,
            "after": self.after,
            "delta": self.delta,
        }


@dataclass(frozen=True)
class RunSummaryComparison:
    """Deterministic comparison between two run summary mappings."""

    status: str
    metrics: list[MetricComparison]
    notes: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "notes": list(self.notes),
        }


def compare_run_summaries(
    before_summary: dict[str, Any],
    after_summary: dict[str, Any],
) -> RunSummaryComparison:
    """Compare two run summary dictionaries without reading or writing files."""
    before = _extract_metrics(before_summary)
    after = _extract_metrics(after_summary)
    metrics: list[MetricComparison] = []
    notes: list[str] = []

    for metric in NUMERIC_METRICS:
        before_value = before.get(metric)
        after_value = after.get(metric)
        delta = (
            after_value - before_value
            if isinstance(before_value, int)
            and not isinstance(before_value, bool)
            and isinstance(after_value, int)
            and not isinstance(after_value, bool)
            else None
        )
        if before_value is None or after_value is None:
            notes.append(f"{metric}: missing in one or both summaries")
        metrics.append(MetricComparison(metric, before_value, after_value, delta))

    for metric in STRING_METRICS:
        before_value = before.get(metric)
        after_value = after.get(metric)
        if before_value is None or after_value is None:
            notes.append(f"{metric}: missing in one or both summaries")
        metrics.append(MetricComparison(metric, before_value, after_value, None))

    return RunSummaryComparison(
        status="WARN" if notes else "PASS",
        metrics=metrics,
        notes=notes or ["all comparison metrics available"],
    )


def render_run_comparison_markdown(comparison: RunSummaryComparison) -> str:
    """Render a deterministic Markdown comparison table."""
    if not isinstance(comparison, RunSummaryComparison):
        raise ValueError("comparison must be a RunSummaryComparison.")
    lines = [
        "# AI Release Radar Run Comparison",
        "",
        f"- [F] Comparison status: {comparison.status}.",
        "",
        "| Metric | Before | After | Delta |",
        "|---|---:|---:|---:|",
    ]
    for metric in comparison.metrics:
        lines.append(
            "| "
            f"{metric.metric} | "
            f"{_value_label(metric.before)} | "
            f"{_value_label(metric.after)} | "
            f"{_value_label(metric.delta)} |"
        )
    lines.extend(["", "## Notes", ""])
    for note in comparison.notes:
        lines.append(f"- [F] {note}.")
    return "\n".join(lines).rstrip("\n") + "\n"


def _extract_metrics(summary: dict[str, Any]) -> dict[str, int | str | None]:
    if not isinstance(summary, dict):
        raise ValueError("summary must be a dict.")
    result = _mapping(summary.get("result"))
    source_diagnostics = _source_diagnostics(summary)
    action_counts = _mapping(result.get("project_action_counts"))
    report_scorecard = _mapping(summary.get("report_scorecard"))
    return {
        "sources_checked": _int_or_none(result.get("source_count")),
        "parsed_sources": _int_or_none(result.get("parsed_count")),
        "items": _int_or_none(result.get("item_count")),
        "project_impacts": _int_or_none(result.get("project_impact_count")),
        "direct_actions": _int_or_none(
            result.get("direct_action_count", action_counts.get("direct_action"))
        ),
        "monitor_only_actions": _int_or_none(
            result.get("monitor_only_action_count", action_counts.get("monitor_only"))
        ),
        "failed_sources": _int_or_none(result.get("failed_count")),
        "unsupported_sources": _int_or_none(
            result.get("unsupported_source_count", _count_unsupported(source_diagnostics))
        ),
        "scorecard_result": _str_or_none(
            result.get("report_scorecard_status", report_scorecard.get("status"))
        ),
    }


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _source_diagnostics(summary: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = summary.get("source_diagnostics")
    if isinstance(candidates, list):
        return [candidate for candidate in candidates if isinstance(candidate, dict)]
    live_snapshot = _mapping(summary.get("live_snapshot"))
    candidates = live_snapshot.get("source_diagnostics")
    if isinstance(candidates, list):
        return [candidate for candidate in candidates if isinstance(candidate, dict)]
    return []


def _count_unsupported(source_diagnostics: list[dict[str, Any]]) -> int:
    return sum(
        1
        for source in source_diagnostics
        if source.get("diagnostic_status") == "fetched_but_unsupported"
        or source.get("parser_status") == "parser_skipped_unsupported_source"
    )


def _int_or_none(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _str_or_none(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None


def _value_label(value: int | str | None) -> str:
    if value is None:
        return "n/a"
    return str(value)

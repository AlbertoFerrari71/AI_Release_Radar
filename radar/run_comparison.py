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


@dataclass(frozen=True)
class MultiDayRunComparison:
    """Noise-control comparison across ordered daily run summaries."""

    status: str
    new_today: list[str]
    repeated_items: list[str]
    stale_actions: list[str]
    persistent_source_warnings: list[str]
    coverage_unchanged: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "status": self.status,
            "new_today": list(self.new_today),
            "repeated_items": list(self.repeated_items),
            "stale_actions": list(self.stale_actions),
            "persistent_source_warnings": list(self.persistent_source_warnings),
            "coverage_unchanged": self.coverage_unchanged,
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


def compare_multi_day_runs(summaries: list[dict[str, Any]]) -> MultiDayRunComparison:
    """Compare ordered run summaries for repeated items, actions and warnings."""
    if len(summaries) < 2:
        raise ValueError("at least two run summaries are required.")
    previous_summaries = summaries[:-1]
    latest = summaries[-1]
    previous_items = set().union(*(_observed_item_ids(summary) for summary in previous_summaries))
    latest_items = _observed_item_ids(latest)
    new_today = sorted(latest_items - previous_items)
    repeated_items = sorted(latest_items & previous_items)
    stale_actions = _stale_actions(previous_summaries, latest)
    persistent_warnings = _persistent_source_warnings(previous_summaries, latest)
    coverage_unchanged = _coverage_tuple(previous_summaries[-1]) == _coverage_tuple(latest)
    status = "PASS" if new_today or repeated_items or stale_actions or persistent_warnings else "WARN"
    return MultiDayRunComparison(
        status=status,
        new_today=new_today,
        repeated_items=repeated_items,
        stale_actions=stale_actions,
        persistent_source_warnings=persistent_warnings,
        coverage_unchanged=coverage_unchanged,
    )


def render_multi_day_comparison_markdown(comparison: MultiDayRunComparison) -> str:
    """Render multi-day noise-control comparison as Markdown."""
    if not isinstance(comparison, MultiDayRunComparison):
        raise ValueError("comparison must be a MultiDayRunComparison.")
    lines = [
        "# 0690) Multi-Day Run Comparison",
        "",
        f"- [F] status: {comparison.status}.",
        f"- [F] coverage_unchanged: {comparison.coverage_unchanged}.",
        "",
        "## New Today",
        "",
        *_bullet_lines(comparison.new_today),
        "",
        "## Repeated Items",
        "",
        *_bullet_lines(comparison.repeated_items),
        "",
        "## Stale Actions",
        "",
        *_bullet_lines(comparison.stale_actions),
        "",
        "## Persistent Source Warnings",
        "",
        *_bullet_lines(comparison.persistent_source_warnings),
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


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


def _observed_item_ids(summary: dict[str, Any]) -> set[str]:
    result = _mapping(summary.get("result"))
    explicit = result.get("item_ids")
    if isinstance(explicit, list):
        return {item for item in explicit if isinstance(item, str) and item.strip()}
    diff_result = _mapping(summary.get("diff_result"))
    item_ids: set[str] = set()
    for key in ("new_items", "changed_items", "removed_items", "repeated_items"):
        values = diff_result.get(key)
        if isinstance(values, list):
            item_ids.update(item for item in values if isinstance(item, str) and item.strip())
    impacts = result.get("project_impacts")
    if isinstance(impacts, list):
        for impact in impacts:
            raw = _mapping(impact)
            item_id = raw.get("item_id")
            if isinstance(item_id, str) and item_id.strip():
                item_ids.add(item_id)
    return item_ids


def _stale_actions(
    previous_summaries: list[dict[str, Any]],
    latest: dict[str, Any],
) -> list[str]:
    previous_action_ids = set().union(*(_action_ids(summary) for summary in previous_summaries))
    latest_action_ids = _action_ids(latest)
    repeated = sorted(previous_action_ids & latest_action_ids)
    if repeated:
        return repeated
    previous_direct = any(
        (_extract_metrics(summary).get("direct_actions") or 0) > 0
        for summary in previous_summaries
    )
    latest_direct = (_extract_metrics(latest).get("direct_actions") or 0) > 0
    return ["direct_actions_repeated"] if previous_direct and latest_direct else []


def _action_ids(summary: dict[str, Any]) -> set[str]:
    result = _mapping(summary.get("result"))
    impacts = result.get("project_impacts")
    if not isinstance(impacts, list):
        return set()
    action_ids: set[str] = set()
    for impact in impacts:
        raw = _mapping(impact)
        if raw.get("action_type") == "direct_action":
            item_id = _str_or_none(raw.get("item_id"))
            project_key = _str_or_none(raw.get("project_key"))
            if item_id and project_key:
                action_ids.add(f"{project_key}:{item_id}")
    return action_ids


def _persistent_source_warnings(
    previous_summaries: list[dict[str, Any]],
    latest: dict[str, Any],
) -> list[str]:
    previous = set().union(*(_source_warning_ids(summary) for summary in previous_summaries))
    current = _source_warning_ids(latest)
    return sorted(previous & current)


def _source_warning_ids(summary: dict[str, Any]) -> set[str]:
    warnings: set[str] = set()
    for source in _source_diagnostics(summary):
        source_id = _str_or_none(source.get("source_id")) or "unknown_source"
        status = _str_or_none(source.get("diagnostic_status") or source.get("parser_status"))
        if status and status not in {"parsed", "ok"}:
            warnings.add(f"{source_id}:{status}")
    return warnings


def _coverage_tuple(summary: dict[str, Any]) -> tuple[int | None, int | None]:
    metrics = _extract_metrics(summary)
    return metrics.get("sources_checked"), metrics.get("parsed_sources")


def _bullet_lines(values: list[str]) -> list[str]:
    if not values:
        return ["- [F] none"]
    return [f"- [F] {value}" for value in values]


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

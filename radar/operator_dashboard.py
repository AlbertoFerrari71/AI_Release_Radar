"""Compact daily operator dashboard rendering."""

from __future__ import annotations

from typing import Any


def render_operator_dashboard(
    run_summary: object,
    *,
    daily_quality_gate: object,
    action_triage: object,
    prompt_suggestions: object,
    hag_status: str,
    scheduler_status: str | None = None,
) -> str:
    """Render the compact operator dashboard Markdown."""
    result = _result(run_summary)
    quality = _mapping(daily_quality_gate)
    triage = _mapping(action_triage)
    prompt_pack = _mapping(prompt_suggestions)
    counts = _mapping(triage.get("counts"))
    lines = [
        "# 0710) Daily Operator Dashboard",
        "",
        f"- [F] run_status: {result.get('status')}.",
        f"- [F] gate: {quality.get('overall_daily_review_status')}.",
        f"- [F] scheduler_status: {scheduler_status or 'dry-report only / unchanged'}.",
        f"- [F] source_coverage: {quality.get('source_coverage_status')}.",
        f"- [F] parsed_sources: {result.get('parsed_count')}/{result.get('source_count')}.",
        f"- [F] new_meaningful_items: {result.get('new_count', result.get('item_count'))}.",
        f"- [F] direct_actions: {result.get('direct_action_count')}.",
        f"- [F] monitor_only_summary: {result.get('monitor_only_action_count')}.",
        f"- [F] prompt_suggestions: {prompt_pack.get('suggestions_count', 0)}.",
        f"- [F] manual_review_queue: {counts.get('manual_review', 0)}.",
        f"- [F] HAG: {hag_status}.",
        "- [F] no_auto_action: confirmed.",
        "",
        "## Next Step",
        "",
        "- [PROP] Alberto reviews HAG decisions and approves at most one suggested prompt as a separate step.",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def _result(run_summary: object) -> dict[str, Any]:
    raw = _mapping(run_summary)
    return _mapping(raw.get("result") or raw.get("real_run") or run_summary)


def _mapping(value: object) -> dict[str, Any]:
    if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
        value = value.to_dict()
    return value if isinstance(value, dict) else {}

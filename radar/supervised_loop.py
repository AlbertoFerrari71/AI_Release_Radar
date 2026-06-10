"""Supervised action loop dry-run rendering."""

from __future__ import annotations

from typing import Any


def render_supervised_action_loop_dry_run(
    *,
    action_triage: object,
    prompt_suggestions: object,
    hag_status: str,
    dashboard_path: str,
) -> str:
    """Render a dry-run report for the supervised action loop."""
    triage = _mapping(action_triage)
    prompt_pack = _mapping(prompt_suggestions)
    counts = _mapping(triage.get("counts"))
    lines = [
        "# 0730) Supervised Action Loop Dry Run",
        "",
        "- [F] mode: dry_run.",
        "- [F] actions_executed: false.",
        "- [F] prompt_suggestions_executed: false.",
        "- [F] other_repositories_touched: false.",
        "- [F] email_sent: false.",
        "- [F] llm_called: false.",
        f"- [F] HAG status: {hag_status}.",
        f"- [F] dashboard_path: {dashboard_path}.",
        "",
        "## Triage Counts",
        "",
    ]
    for key in sorted(counts):
        lines.append(f"- [F] {key}: {counts[key]}")
    lines.extend(
        [
            "",
            "## Prompt Suggestions",
            "",
            f"- [F] suggestions_count: {prompt_pack.get('suggestions_count', 0)}.",
            "- [F] status: suggested_only.",
            "",
            "## Operator Decision",
            "",
            "- [PROP] Continue only after Alberto approves a specific follow-up step.",
        ]
    )
    return "\n".join(lines).rstrip("\n") + "\n"


def _mapping(value: object) -> dict[str, Any]:
    if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
        value = value.to_dict()
    return value if isinstance(value, dict) else {}

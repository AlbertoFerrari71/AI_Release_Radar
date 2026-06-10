"""Human Approval Gate report rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from radar.action_triage import ActionTriageResult
from radar.daily_quality_gate import ACTION_REVIEW_REQUIRED, FAIL, HOLD
from radar.prompt_suggestions import PromptSuggestionPack


@dataclass(frozen=True)
class HumanApprovalGateReport:
    """Serializable Human Approval Gate summary."""

    status: str
    decisions: list[str]
    markdown: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "status": self.status,
            "decisions": list(self.decisions),
            "markdown": self.markdown,
        }


def build_hag_report(
    run_summary: object,
    *,
    daily_quality_gate: object,
    action_triage: ActionTriageResult | dict[str, Any],
    prompt_suggestions: PromptSuggestionPack | dict[str, Any],
) -> HumanApprovalGateReport:
    """Build a deterministic Human Approval Gate report."""
    result = _result(run_summary)
    quality = _mapping(daily_quality_gate)
    triage = _triage_dict(action_triage)
    prompt_pack = _prompt_dict(prompt_suggestions)
    status = _hag_status(quality, triage, prompt_pack)
    decisions = [
        "A: approve one suggested prompt as a separate Codex step",
        "B: keep item in monitor-only queue",
        "C: request source coverage improvement before action",
        "D: stop and open a fix-only step if gate failed",
    ]
    markdown = _render_markdown(result, quality, triage, prompt_pack, status, decisions)
    return HumanApprovalGateReport(status=status, decisions=decisions, markdown=markdown)


def _render_markdown(
    result: dict[str, Any],
    quality: dict[str, Any],
    triage: dict[str, Any],
    prompt_pack: dict[str, Any],
    status: str,
    decisions: list[str],
) -> str:
    counts = _mapping(triage.get("counts"))
    lines = [
        "# 0680) Human Approval Gate Report",
        "",
        f"- [F] HAG status: {status}.",
        f"- [F] run_status: {result.get('status')}.",
        f"- [F] overall_daily_review_status: {quality.get('overall_daily_review_status')}.",
        f"- [F] automation_gate_status: {quality.get('automation_gate_status', 'see daily summary')}.",
        "- [F] auto_actions_executed: false.",
        "- [F] emails_sent: false.",
        "- [F] llm_called: false.",
        "",
        "## What Happened",
        "",
        f"- [F] sources_checked: {result.get('source_count')}.",
        f"- [F] parsed_sources: {result.get('parsed_count')}.",
        f"- [F] items_found: {result.get('item_count')}.",
        f"- [F] direct_actions: {result.get('direct_action_count')}.",
        f"- [F] monitor_only_actions: {result.get('monitor_only_action_count')}.",
        "",
        "## What Matters",
        "",
        f"- [F] codex_prompt_candidate: {counts.get('codex_prompt_candidate', 0)}.",
        f"- [F] blocked_by_coverage: {counts.get('blocked_by_coverage', 0)}.",
        f"- [F] blocked_by_manual_review: {counts.get('blocked_by_manual_review', 0)}.",
        f"- [F] manual_review: {counts.get('manual_review', 0)}.",
        "",
        "## Prompt Suggestions",
        "",
        f"- [F] suggestions_count: {prompt_pack.get('suggestions_count', 0)}.",
        "- [F] suggestions_status: suggested_only.",
        "",
        "## Forbidden Automatically",
        "",
        "- [F] Do not modify other repositories.",
        "- [F] Do not open cross-project PRs.",
        "- [F] Do not send email or notifications.",
        "- [F] Do not call LLM APIs.",
        "- [F] Do not execute prompt suggestions automatically.",
        "",
        "## Decisions",
        "",
    ]
    lines.extend(f"- [PROP] {decision}." for decision in decisions)
    return "\n".join(lines).rstrip("\n") + "\n"


def _hag_status(
    quality: dict[str, Any],
    triage: dict[str, Any],
    prompt_pack: dict[str, Any],
) -> str:
    if quality.get("overall_daily_review_status") == FAIL:
        return "FAIL_STOP"
    counts = _mapping(triage.get("counts"))
    if counts.get("blocked_by_coverage") or counts.get("blocked_by_manual_review"):
        return "HOLD_FOR_HUMAN_APPROVAL"
    if quality.get("overall_daily_review_status") in {ACTION_REVIEW_REQUIRED, HOLD}:
        return "HUMAN_APPROVAL_REQUIRED"
    if prompt_pack.get("suggestions_count"):
        return "HUMAN_APPROVAL_REQUIRED"
    return "NO_ACTION_REQUIRED"


def _result(run_summary: object) -> dict[str, Any]:
    raw = _mapping(run_summary)
    return _mapping(raw.get("result") or raw.get("real_run") or run_summary)


def _triage_dict(triage: ActionTriageResult | dict[str, Any]) -> dict[str, Any]:
    if isinstance(triage, ActionTriageResult):
        return triage.to_dict()
    return _mapping(triage)


def _prompt_dict(prompt_suggestions: PromptSuggestionPack | dict[str, Any]) -> dict[str, Any]:
    if isinstance(prompt_suggestions, PromptSuggestionPack):
        return prompt_suggestions.to_dict()
    return _mapping(prompt_suggestions)


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

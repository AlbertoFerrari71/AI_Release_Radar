"""Suggested-only Codex prompt pack generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from radar.action_triage import ActionTriageResult, TriageEntry


SUGGESTED_ONLY = "suggested_only"


@dataclass(frozen=True)
class PromptSuggestion:
    """One suggested Codex prompt, never executed by this module."""

    title: str
    target_project: str
    reason: str
    risk_class: str
    suggested_step_number: str
    prompt_path: str | None
    status: str = SUGGESTED_ONLY
    prompt_text: str | None = None

    def __post_init__(self) -> None:
        if self.status != SUGGESTED_ONLY:
            raise ValueError("prompt suggestion status must be suggested_only.")

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "target_project": self.target_project,
            "reason": self.reason,
            "risk_class": self.risk_class,
            "suggested_step_number": self.suggested_step_number,
            "prompt_path": self.prompt_path,
            "status": self.status,
            "prompt_text": self.prompt_text,
        }


@dataclass(frozen=True)
class PromptSuggestionPack:
    """Serializable pack of suggested-only prompts."""

    suggestions: list[PromptSuggestion]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "suggestions": [suggestion.to_dict() for suggestion in self.suggestions],
            "warnings": list(self.warnings),
            "suggestions_count": len(self.suggestions),
            "status": SUGGESTED_ONLY,
        }


def suggest_codex_prompts(
    triage: ActionTriageResult | dict[str, Any],
    *,
    max_suggestions: int = 5,
) -> PromptSuggestionPack:
    """Create suggested-only prompt entries from a triage result."""
    entries = _entries(triage)
    warnings: list[str] = []
    suggestions: list[PromptSuggestion] = []
    for entry in entries:
        if len(suggestions) >= max_suggestions:
            warnings.append("prompt_suggestion_limit_reached")
            break
        suggestion = _suggestion_for_entry(entry, len(suggestions) + 1)
        if suggestion is None:
            continue
        suggestions.append(suggestion)
    if not suggestions:
        warnings.append("no_prompt_suggestions_generated")
    return PromptSuggestionPack(suggestions=suggestions, warnings=sorted(set(warnings)))


def render_prompt_suggestion_pack_markdown(pack: PromptSuggestionPack) -> str:
    """Render suggested-only prompt suggestions as Markdown."""
    lines = [
        "# 0660) Codex Prompt Suggestion Pack",
        "",
        "- [F] status: suggested_only.",
        f"- [F] suggestions_count: {len(pack.suggestions)}.",
        "- [F] prompts_executed: false.",
        "- [F] other_repositories_modified: false.",
        "",
        "## Suggestions",
        "",
    ]
    if pack.suggestions:
        for suggestion in pack.suggestions:
            lines.extend(
                [
                    f"### {suggestion.suggested_step_number} - {suggestion.title}",
                    "",
                    f"- [F] target_project: {suggestion.target_project}.",
                    f"- [F] risk_class: {suggestion.risk_class}.",
                    f"- [F] status: {suggestion.status}.",
                    f"- [F] prompt_path: {suggestion.prompt_path or 'not_generated'}",
                    f"- [INT] reason: {suggestion.reason}.",
                    "",
                ]
            )
            if suggestion.prompt_text:
                lines.extend(["```text", suggestion.prompt_text.rstrip(), "```", ""])
    else:
        lines.append("- [F] none")
    lines.extend(["## Warnings", ""])
    if pack.warnings:
        lines.extend(f"- [F] {warning}" for warning in pack.warnings)
    else:
        lines.append("- [F] none")
    return "\n".join(lines).rstrip("\n") + "\n"


def _entries(triage: ActionTriageResult | dict[str, Any]) -> list[TriageEntry]:
    if isinstance(triage, ActionTriageResult):
        return list(triage.entries)
    raw_entries = triage.get("entries") if isinstance(triage, dict) else None
    if not isinstance(raw_entries, list):
        return []
    entries = []
    for raw in raw_entries:
        if not isinstance(raw, dict):
            continue
        entries.append(
            TriageEntry(
                triage_class=str(raw.get("triage_class")),
                title=str(raw.get("title") or "Radar action"),
                target_project=str(raw.get("target_project") or "Ambiguous project"),
                project_key=raw.get("project_key") if isinstance(raw.get("project_key"), str) else None,
                reason=str(raw.get("reason") or "triage signal"),
                risk_class=str(raw.get("risk_class") or "L1/L2"),
                item_category=raw.get("item_category") if isinstance(raw.get("item_category"), str) else None,
                severity=raw.get("severity") if isinstance(raw.get("severity"), str) else None,
                score=raw.get("score") if isinstance(raw.get("score"), int) else None,
                count=raw.get("count") if isinstance(raw.get("count"), int) else 1,
            )
        )
    return entries


def _suggestion_for_entry(entry: TriageEntry, index: int) -> PromptSuggestion | None:
    if entry.triage_class in {"ignore", "monitor"}:
        return None
    step_number = f"PS-{index:03d}"
    if entry.project_key is None:
        title = f"Review ambiguous radar signal: {entry.title}"
        target_project = entry.target_project
        prompt_text = (
            "Review the radar item manually before creating any project work.\n"
            "Do not modify another repository, do not open a PR, and do not execute actions.\n"
            f"Reason: {entry.reason}."
        )
    elif entry.triage_class == "codex_prompt_candidate":
        title = f"Prepare scoped Codex review for {entry.target_project}"
        target_project = entry.target_project
        prompt_text = (
            f"Target project: {entry.target_project}\n"
            "Mode: proposal only until Alberto approves.\n"
            f"Radar reason: {entry.reason}\n"
            "Task: inspect impact and propose a narrow Codex step. Do not commit, push, "
            "open PRs, send notifications, call LLM APIs, or touch other repositories."
        )
    elif entry.triage_class == "blocked_by_coverage":
        title = f"Review coverage before action for {entry.target_project}"
        target_project = entry.target_project
        prompt_text = (
            f"Target project: {entry.target_project}\n"
            "Mode: coverage review only.\n"
            f"Radar reason: {entry.reason}\n"
            "Task: verify whether the radar signal is sufficiently sourced before any "
            "implementation prompt is drafted."
        )
    else:
        title = f"Human approval review for {entry.target_project}"
        target_project = entry.target_project
        prompt_text = (
            f"Target project: {entry.target_project}\n"
            "Mode: Human Approval Gate review.\n"
            f"Radar reason: {entry.reason}\n"
            "Task: decide whether this should become a separate Codex step. No execution."
        )
    return PromptSuggestion(
        title=title,
        target_project=target_project,
        reason=entry.reason,
        risk_class=entry.risk_class,
        suggested_step_number=step_number,
        prompt_path=None,
        prompt_text=prompt_text,
    )

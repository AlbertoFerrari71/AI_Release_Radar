"""Deterministic quality scorecard for rendered radar report inputs."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from radar.project_impact import ACTION_TYPE_RANK, ProjectImpact
from radar.report_engine import ReportInput


SCORECARD_STATUSES = ("PASS", "WARN", "FAIL")
SCORECARD_CHECKS = (
    "has_readable_titles",
    "has_source_links",
    "has_parsed_source_count",
    "has_source_diagnostics",
    "has_actionable_project_actions",
    "has_no_item_id_only_top_actions",
    "has_noise_control",
    "has_next_step",
)
_ITEM_ID_ONLY_ACTION_RE = re.compile(r"^`?[\w.-]+`?$")


@dataclass(frozen=True)
class ScorecardFinding:
    """One deterministic report-quality check result."""

    check: str
    status: str
    message: str

    def __post_init__(self) -> None:
        if self.check not in SCORECARD_CHECKS:
            raise ValueError(f"unsupported scorecard check: {self.check}")
        if self.status not in SCORECARD_STATUSES:
            raise ValueError(f"unsupported scorecard status: {self.status}")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string.")

    def to_dict(self) -> dict[str, str]:
        return {
            "check": self.check,
            "status": self.status,
            "message": self.message,
        }


@dataclass(frozen=True)
class ReportScorecard:
    """Overall deterministic report scorecard."""

    status: str
    findings: list[ScorecardFinding]

    def __post_init__(self) -> None:
        if self.status not in SCORECARD_STATUSES:
            raise ValueError(f"unsupported scorecard status: {self.status}")
        if not isinstance(self.findings, list) or not self.findings:
            raise ValueError("findings must be a non-empty list.")
        for finding in self.findings:
            if not isinstance(finding, ScorecardFinding):
                raise ValueError("findings must contain ScorecardFinding entries.")

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def evaluate_report_scorecard(
    report_input: ReportInput,
    *,
    live_result: dict[str, Any] | None = None,
    source_diagnostics: list[dict[str, Any]] | None = None,
    next_step: str | None = None,
) -> ReportScorecard:
    """Evaluate deterministic quality checks for one prepared report input."""
    if not isinstance(report_input, ReportInput):
        raise ValueError("report_input must be a ReportInput.")
    findings = [
        _check_readable_titles(report_input),
        _check_source_links(report_input),
        _check_parsed_source_count(live_result),
        _check_source_diagnostics(source_diagnostics),
        _check_actionable_project_actions(report_input.project_impacts),
        _check_no_item_id_only_top_actions(report_input.project_impacts),
        _check_noise_control(report_input.project_impacts, source_diagnostics),
        _check_next_step(next_step),
    ]
    return ReportScorecard(
        status=_overall_status(findings),
        findings=findings,
    )


def render_scorecard_markdown(scorecard: ReportScorecard) -> list[str]:
    """Render scorecard findings as deterministic Markdown bullet lines."""
    if not isinstance(scorecard, ReportScorecard):
        raise ValueError("scorecard must be a ReportScorecard.")
    lines = [f"- [F] Scorecard status: {scorecard.status}."]
    for finding in scorecard.findings:
        lines.append(f"- [F] {finding.check}: {finding.status} - {finding.message}")
    return lines


def _check_readable_titles(report_input: ReportInput) -> ScorecardFinding:
    changed_ids = _changed_item_ids(report_input)
    if not changed_ids:
        return ScorecardFinding(
            "has_readable_titles",
            "PASS",
            "no changed items require titles",
        )
    unreadable = []
    for item_id in changed_ids:
        item = report_input.items_by_id[item_id]
        if not item.title.strip() or item.title.strip() == item.item_id:
            unreadable.append(item_id)
    if unreadable:
        return ScorecardFinding(
            "has_readable_titles",
            "FAIL",
            f"unreadable title count {len(unreadable)}",
        )
    return ScorecardFinding(
        "has_readable_titles",
        "PASS",
        f"{len(changed_ids)} changed item title(s) are readable",
    )


def _check_source_links(report_input: ReportInput) -> ScorecardFinding:
    changed_ids = _changed_item_ids(report_input)
    missing = []
    for item_id in changed_ids:
        item = report_input.items_by_id[item_id]
        if not item.url.startswith(("http://", "https://")):
            missing.append(item_id)
    if missing:
        return ScorecardFinding(
            "has_source_links",
            "WARN",
            f"source link missing for {len(missing)} changed item(s)",
        )
    return ScorecardFinding(
        "has_source_links",
        "PASS",
        "changed items include source links",
    )


def _check_parsed_source_count(live_result: dict[str, Any] | None) -> ScorecardFinding:
    if live_result is None:
        return ScorecardFinding(
            "has_parsed_source_count",
            "WARN",
            "no live-result parsed source count was provided",
        )
    parsed_count = live_result.get("parsed_count")
    if not isinstance(parsed_count, int) or isinstance(parsed_count, bool):
        return ScorecardFinding(
            "has_parsed_source_count",
            "FAIL",
            "parsed_count is missing or not an integer",
        )
    return ScorecardFinding(
        "has_parsed_source_count",
        "PASS",
        f"parsed_count={parsed_count}",
    )


def _check_source_diagnostics(
    source_diagnostics: list[dict[str, Any]] | None,
) -> ScorecardFinding:
    if not source_diagnostics:
        return ScorecardFinding(
            "has_source_diagnostics",
            "WARN",
            "source diagnostics were not provided",
        )
    missing_status = [
        source
        for source in source_diagnostics
        if not isinstance(source.get("diagnostic_status"), str)
    ]
    if missing_status:
        return ScorecardFinding(
            "has_source_diagnostics",
            "WARN",
            f"{len(missing_status)} source diagnostic(s) lack diagnostic_status",
        )
    return ScorecardFinding(
        "has_source_diagnostics",
        "PASS",
        f"{len(source_diagnostics)} source diagnostic(s) include status",
    )


def _check_actionable_project_actions(
    project_impacts: list[ProjectImpact],
) -> ScorecardFinding:
    if not project_impacts:
        return ScorecardFinding(
            "has_actionable_project_actions",
            "WARN",
            "no project impacts are available",
        )
    missing_actions = [
        impact
        for impact in project_impacts
        if not impact.suggested_actions or impact.action_type not in ACTION_TYPE_RANK
    ]
    if missing_actions:
        return ScorecardFinding(
            "has_actionable_project_actions",
            "FAIL",
            f"{len(missing_actions)} project impact(s) lack valid actions",
        )
    if all(impact.action_type == "no_action" for impact in project_impacts):
        return ScorecardFinding(
            "has_actionable_project_actions",
            "WARN",
            "only no_action impacts are available",
        )
    return ScorecardFinding(
        "has_actionable_project_actions",
        "PASS",
        f"{len(project_impacts)} project impact action(s) available",
    )


def _check_no_item_id_only_top_actions(
    project_impacts: list[ProjectImpact],
) -> ScorecardFinding:
    item_id_only_count = 0
    for impact in project_impacts:
        for action in impact.suggested_actions:
            if _ITEM_ID_ONLY_ACTION_RE.match(action.strip()):
                item_id_only_count += 1
    if item_id_only_count:
        return ScorecardFinding(
            "has_no_item_id_only_top_actions",
            "FAIL",
            f"{item_id_only_count} action(s) are item-id-only",
        )
    return ScorecardFinding(
        "has_no_item_id_only_top_actions",
        "PASS",
        "project actions are descriptive",
    )


def _check_noise_control(
    project_impacts: list[ProjectImpact],
    source_diagnostics: list[dict[str, Any]] | None,
) -> ScorecardFinding:
    has_action_types = bool(project_impacts) and all(
        impact.action_type in ACTION_TYPE_RANK for impact in project_impacts
    )
    has_diagnostic_statuses = bool(source_diagnostics) and all(
        isinstance(source.get("diagnostic_status"), str) for source in source_diagnostics
    )
    if has_action_types and has_diagnostic_statuses:
        return ScorecardFinding(
            "has_noise_control",
            "PASS",
            "action_type and diagnostic_status are available",
        )
    if has_action_types or has_diagnostic_statuses:
        return ScorecardFinding(
            "has_noise_control",
            "WARN",
            "only one noise-control signal is available",
        )
    return ScorecardFinding(
        "has_noise_control",
        "FAIL",
        "no action_type or diagnostic_status signal is available",
    )


def _check_next_step(next_step: str | None) -> ScorecardFinding:
    if isinstance(next_step, str) and next_step.strip():
        return ScorecardFinding(
            "has_next_step",
            "PASS",
            "next step is present",
        )
    return ScorecardFinding(
        "has_next_step",
        "WARN",
        "next step was not provided to the scorecard",
    )


def _changed_item_ids(report_input: ReportInput) -> list[str]:
    return sorted(
        set(report_input.diff_result.new_items)
        | set(report_input.diff_result.changed_items)
        | set(report_input.diff_result.removed_items)
    )


def _overall_status(findings: list[ScorecardFinding]) -> str:
    statuses = {finding.status for finding in findings}
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"

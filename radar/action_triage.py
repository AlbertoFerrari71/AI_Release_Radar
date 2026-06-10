"""Deterministic action triage for supervised daily review."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from radar.daily_quality_gate import ACTION_REVIEW_REQUIRED, FAIL, HOLD, PASS, WARN


TRIAGE_CLASSES = (
    "ignore",
    "monitor",
    "manual_review",
    "codex_prompt_candidate",
    "blocked_by_coverage",
    "blocked_by_manual_review",
)


@dataclass(frozen=True)
class TriageEntry:
    """One triaged action or review item."""

    triage_class: str
    title: str
    target_project: str
    project_key: str | None
    reason: str
    risk_class: str
    item_category: str | None = None
    severity: str | None = None
    score: int | None = None
    count: int = 1

    def __post_init__(self) -> None:
        if self.triage_class not in TRIAGE_CLASSES:
            raise ValueError(f"unsupported triage_class: {self.triage_class}")
        if self.count < 1:
            raise ValueError("count must be positive.")

    def to_dict(self) -> dict[str, object]:
        return {
            "triage_class": self.triage_class,
            "title": self.title,
            "target_project": self.target_project,
            "project_key": self.project_key,
            "reason": self.reason,
            "risk_class": self.risk_class,
            "item_category": self.item_category,
            "severity": self.severity,
            "score": self.score,
            "count": self.count,
        }


@dataclass(frozen=True)
class ActionTriageResult:
    """Serializable action triage result."""

    status: str
    entries: list[TriageEntry]
    counts: dict[str, int]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "status": self.status,
            "entries": [entry.to_dict() for entry in self.entries],
            "counts": dict(self.counts),
            "warnings": list(self.warnings),
        }


def triage_daily_actions(
    run_summary: object,
    *,
    automation_gate: object | None = None,
    daily_quality_gate: object | None = None,
    project_profiles: dict[str, object] | None = None,
) -> ActionTriageResult:
    """Classify actions without executing any action."""
    summary = _mapping(run_summary)
    result = _mapping(summary.get("result") or summary.get("real_run") or run_summary)
    gate = _mapping(automation_gate or summary.get("automation_gate"))
    quality = _mapping(daily_quality_gate or summary.get("daily_quality_gate_v2"))
    metrics = _merge_metrics(result, gate)
    warnings: list[str] = []
    entries = _explicit_entries(result, metrics, gate, quality, project_profiles, warnings)
    if not entries:
        entries = _aggregate_entries(metrics, gate, quality, warnings)
    entries.extend(_manual_review_entries(gate))
    entries = sorted(entries, key=lambda entry: (entry.triage_class, entry.project_key or "", entry.title))
    counts = {triage_class: 0 for triage_class in TRIAGE_CLASSES}
    for entry in entries:
        counts[entry.triage_class] += entry.count
    status = _triage_status(counts)
    return ActionTriageResult(
        status=status,
        entries=entries,
        counts=counts,
        warnings=sorted(set(warnings)),
    )


def _explicit_entries(
    result: dict[str, Any],
    metrics: dict[str, object],
    gate: dict[str, Any],
    quality: dict[str, Any],
    project_profiles: dict[str, object] | None,
    warnings: list[str],
) -> list[TriageEntry]:
    raw_impacts = result.get("project_impacts")
    if not isinstance(raw_impacts, list):
        return []
    entries: list[TriageEntry] = []
    for impact_data in raw_impacts:
        impact = _mapping(impact_data)
        action_type = _str(impact.get("action_type")) or "direct_action"
        category = _str(impact.get("category") or impact.get("item_category"))
        project_key = _str(impact.get("project_key"))
        score = _int_or_none(impact.get("score"))
        profile = _profile(project_profiles, project_key)
        triage_class, reason = _classify_action(
            action_type=action_type,
            category=category,
            score=score,
            profile=profile,
            metrics=metrics,
            gate=gate,
            quality=quality,
        )
        if project_key is None:
            warnings.append("project_key_missing_for_explicit_impact")
        entries.append(
            TriageEntry(
                triage_class=triage_class,
                title=_str(impact.get("title")) or _str(impact.get("item_id")) or "Radar action",
                target_project=_str(impact.get("project_name")) or _project_name(profile) or "Ambiguous project",
                project_key=project_key,
                reason=reason,
                risk_class=_risk_class(project_key, triage_class),
                item_category=category,
                severity=_str(impact.get("severity")),
                score=score,
            )
        )
    return entries


def _aggregate_entries(
    metrics: dict[str, object],
    gate: dict[str, Any],
    quality: dict[str, Any],
    warnings: list[str],
) -> list[TriageEntry]:
    entries: list[TriageEntry] = []
    direct_count = _metric_int(metrics, "direct_action_count")
    monitor_count = _metric_int(metrics, "monitor_only_action_count")
    if direct_count:
        if _coverage_blocks(metrics, quality):
            triage_class = "blocked_by_coverage"
            reason = "direct actions exist, but source coverage is below full-pass threshold"
        elif _manual_review_blocks(gate, metrics, quality):
            triage_class = "blocked_by_manual_review"
            reason = "direct actions require Human Approval Gate before any work"
        else:
            triage_class = "codex_prompt_candidate"
            reason = "direct actions are available for supervised prompt drafting"
        entries.append(
            TriageEntry(
                triage_class=triage_class,
                title="Aggregate direct actions",
                target_project="Mixed project targets",
                project_key=None,
                reason=reason,
                risk_class="L1/L2",
                count=direct_count,
            )
        )
    if monitor_count:
        entries.append(
            TriageEntry(
                triage_class="monitor",
                title="Aggregate monitor-only actions",
                target_project="Mixed project targets",
                project_key=None,
                reason="monitor-only actions stay visible but do not become work automatically",
                risk_class="L1",
                count=monitor_count,
            )
        )
    if not entries:
        warnings.append("no_action_entries_available")
        entries.append(
            TriageEntry(
                triage_class="ignore",
                title="No actionable radar item",
                target_project="none",
                project_key=None,
                reason="no direct or monitor-only actions were found",
                risk_class="L1",
            )
        )
    return entries


def _manual_review_entries(gate: dict[str, Any]) -> list[TriageEntry]:
    queue = gate.get("manual_review_queue")
    if not isinstance(queue, list):
        return []
    entries = []
    for item in queue:
        raw = _mapping(item)
        reason = _str(raw.get("reason")) or "manual_review_required"
        entries.append(
            TriageEntry(
                triage_class="manual_review",
                title=f"Manual review: {_str(raw.get('source_id')) or 'unknown_source'}",
                target_project="Radar source coverage",
                project_key=None,
                reason=reason,
                risk_class="L1/L2",
                severity=_str(raw.get("severity")),
            )
        )
    return entries


def _classify_action(
    *,
    action_type: str,
    category: str | None,
    score: int | None,
    profile: object | None,
    metrics: dict[str, object],
    gate: dict[str, Any],
    quality: dict[str, Any],
) -> tuple[str, str]:
    if _category_in_profile(profile, "ignored_categories", category):
        return "ignore", f"category {category} is ignored for this project"
    if action_type == "no_action":
        return "ignore", "impact was classified as no_action"
    if action_type == "monitor_only" or _category_in_profile(profile, "monitor_categories", category):
        return "monitor", "impact is monitor-only for this project"
    if _coverage_blocks(metrics, quality):
        return "blocked_by_coverage", "source coverage must be reviewed before prompt execution"
    if _manual_review_blocks(gate, metrics, quality):
        return "blocked_by_manual_review", "manual review gate must approve before action"
    threshold = _profile_threshold(profile)
    if score is not None and score < threshold:
        return "monitor", f"score {score} below review_threshold {threshold}"
    return "codex_prompt_candidate", "direct project signal can become a suggested-only Codex prompt"


def _triage_status(counts: dict[str, int]) -> str:
    if counts.get("blocked_by_manual_review") or counts.get("blocked_by_coverage"):
        return HOLD
    if counts.get("codex_prompt_candidate"):
        return ACTION_REVIEW_REQUIRED
    if counts.get("manual_review"):
        return WARN
    return PASS


def _merge_metrics(result: dict[str, Any], gate: dict[str, Any]) -> dict[str, object]:
    gate_metrics = _mapping(gate.get("metrics"))
    metrics = dict(gate_metrics)
    for key in (
        "source_count",
        "parsed_count",
        "direct_action_count",
        "monitor_only_action_count",
        "manual_review_required_count",
        "manual_review_queue_count",
    ):
        if key not in metrics and key in result:
            metrics[key] = result[key]
    source_count = _metric_int(metrics, "source_count")
    parsed_count = _metric_int(metrics, "parsed_count")
    metrics["parsed_ratio"] = round(parsed_count / source_count, 4) if source_count else 0.0
    return metrics


def _coverage_blocks(metrics: dict[str, object], quality: dict[str, Any]) -> bool:
    status = quality.get("source_coverage_status")
    if status in {FAIL, HOLD}:
        return True
    source_count = _metric_int(metrics, "source_count")
    parsed_count = _metric_int(metrics, "parsed_count")
    return source_count > 0 and parsed_count > 0 and parsed_count / source_count < 0.50


def _manual_review_blocks(
    gate: dict[str, Any],
    metrics: dict[str, object],
    quality: dict[str, Any],
) -> bool:
    if gate.get("status") == FAIL:
        return True
    if quality.get("actionability_status") in {ACTION_REVIEW_REQUIRED, HOLD, FAIL}:
        return True
    return _metric_int(metrics, "manual_review_queue_count") > 0


def _profile(project_profiles: dict[str, object] | None, project_key: str | None) -> object | None:
    if project_profiles is None or project_key is None:
        return None
    return project_profiles.get(project_key)


def _profile_threshold(profile: object | None) -> int:
    value = getattr(profile, "review_threshold", None)
    return value if isinstance(value, int) and not isinstance(value, bool) else 60


def _category_in_profile(profile: object | None, attr: str, category: str | None) -> bool:
    if profile is None or category is None:
        return False
    values = getattr(profile, attr, [])
    return isinstance(values, list) and category in values


def _project_name(profile: object | None) -> str | None:
    value = getattr(profile, "project_name", None)
    return value if isinstance(value, str) and value.strip() else None


def _risk_class(project_key: str | None, triage_class: str) -> str:
    if triage_class in {"monitor", "ignore"}:
        return "L1"
    if project_key in {"family_photo_organizer", "controllo_gestione_esolver"}:
        return "L4_REVIEW_ONLY"
    return "L1/L2"


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _metric_int(metrics: dict[str, object], key: str) -> int:
    value = metrics.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value


def _int_or_none(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None

"""Supervised Action Inbox model and Bridge-only dispatch helpers."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from radar.json_utils import write_json


ACTION_TYPES = (
    "review_release",
    "update_skill",
    "check_compatibility",
    "monitor_only",
    "prepare_prompt",
    "no_action",
)
PRIORITIES = ("high", "medium", "low", "monitor")
DECISION_STATUSES = (
    "undecided",
    "approved_for_prompt",
    "deferred",
    "ignored",
    "backlog",
    "review_requested",
)
DECISIONS = ("approve_prompt", "defer", "ignore", "backlog", "request_review")
SAFETY_STATUSES = (
    "safe_prompt_only",
    "requires_human_approval",
    "blocked_auto_action",
)
TREND_STATUSES = (
    "new_today",
    "recurring",
    "already_backlogged",
    "previously_ignored",
    "prompt_already_generated",
)
FORBIDDEN_PREFIXES = ("LAST-", "latest-")
PROMPT_ALLOWED_DECISIONS = {"approved_for_prompt", "review_requested"}
PROMPT_GENERATED_DECISION = "prompt_generated"


@dataclass(frozen=True)
class ActionInboxItem:
    """One supervised candidate action derived from an existing radar run."""

    action_id: str
    action_key: str
    run_id: str
    source_item_id: str
    title: str
    summary: str
    project_key: str | None
    project_name: str
    action_type: str
    priority: str
    priority_score: int
    risk_level: str
    decision_status: str
    safety_status: str
    suggested_prompt_path: str | None
    created_at: str
    updated_at: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    evidence_paths: tuple[str, ...] = field(default_factory=tuple)
    priority_reasons: tuple[str, ...] = field(default_factory=tuple)
    routing_reasons: tuple[str, ...] = field(default_factory=tuple)
    recommended_next_step: str = "Review in Action Center"
    safety_reasons: tuple[str, ...] = field(default_factory=tuple)
    allowed_outputs: tuple[str, ...] = field(default_factory=tuple)
    blocked_outputs: tuple[str, ...] = field(default_factory=tuple)
    human_required: bool = True
    trend_status: str = "new_today"
    trend_reasons: tuple[str, ...] = field(default_factory=tuple)
    noise_status: str = "visible"
    noise_reasons: tuple[str, ...] = field(default_factory=tuple)
    prompt_generation_allowed: bool = False

    def __post_init__(self) -> None:
        if self.action_type not in ACTION_TYPES:
            raise ValueError(f"unsupported action_type: {self.action_type}")
        if self.priority not in PRIORITIES:
            raise ValueError(f"unsupported priority: {self.priority}")
        if self.decision_status not in DECISION_STATUSES:
            raise ValueError(f"unsupported decision_status: {self.decision_status}")
        if self.safety_status not in SAFETY_STATUSES:
            raise ValueError(f"unsupported safety_status: {self.safety_status}")
        if self.trend_status not in TREND_STATUSES:
            raise ValueError(f"unsupported trend_status: {self.trend_status}")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "action_id": self.action_id,
            "action_key": self.action_key,
            "run_id": self.run_id,
            "source_item_id": self.source_item_id,
            "title": self.title,
            "summary": self.summary,
            "project_key": self.project_key,
            "project_name": self.project_name,
            "action_type": self.action_type,
            "priority": self.priority,
            "priority_score": self.priority_score,
            "risk_level": self.risk_level,
            "decision_status": self.decision_status,
            "safety_status": self.safety_status,
            "suggested_prompt_path": self.suggested_prompt_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "reasons": list(self.reasons),
            "evidence_paths": list(self.evidence_paths),
            "priority_reasons": list(self.priority_reasons),
            "routing_reasons": list(self.routing_reasons),
            "recommended_next_step": self.recommended_next_step,
            "safety_reasons": list(self.safety_reasons),
            "allowed_outputs": list(self.allowed_outputs),
            "blocked_outputs": list(self.blocked_outputs),
            "human_required": self.human_required,
            "trend_status": self.trend_status,
            "trend_reasons": list(self.trend_reasons),
            "noise_status": self.noise_status,
            "noise_reasons": list(self.noise_reasons),
            "prompt_generation_allowed": self.prompt_generation_allowed,
        }


@dataclass(frozen=True)
class ActionInbox:
    """Serializable supervised inbox for the dashboard Action Center."""

    run_id: str | None
    actions: tuple[ActionInboxItem, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "schema_version": 1,
            "run_id": self.run_id,
            "actions": [action.to_dict() for action in self.actions],
            "actions_count": len(self.actions),
            "warnings": list(self.warnings),
            "no_auto_action": True,
        }


@dataclass(frozen=True)
class DispatchWriteResult:
    """Result for a Bridge write operation."""

    status: str
    paths: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "status": self.status,
            "paths": list(self.paths),
            "warnings": list(self.warnings),
            "no_auto_action": True,
        }


def build_action_inbox(
    run_details: list[dict[str, Any]],
    *,
    decision_records: list[dict[str, Any]] | None = None,
    now: str | None = None,
) -> ActionInbox:
    """Build the latest-run inbox from read-only run details and decision records."""
    timestamp = now or utc_now()
    if not run_details:
        return ActionInbox(None, (), ("no_run_details_available",))
    latest = run_details[0]
    latest_run = _mapping(latest.get("run"))
    run_id = _string(latest_run.get("run_id")) or "unknown_run"
    records = decision_records or []
    record_index = _decision_record_index(records)
    previous_keys = _previous_action_keys(run_details[1:])
    warnings: list[str] = []
    raw_actions = _raw_actions_from_detail(latest, warnings)
    actions: list[ActionInboxItem] = []
    for raw in raw_actions:
        candidate = _build_action(
            raw,
            latest,
            run_id=run_id,
            timestamp=timestamp,
            previous_keys=previous_keys,
            record_index=record_index,
        )
        actions.append(candidate)
    actions = sorted(
        actions,
        key=lambda action: (
            _priority_rank(action.priority),
            -action.priority_score,
            action.project_name,
            action.title,
        ),
    )
    return ActionInbox(run_id, tuple(actions), tuple(sorted(set(warnings))))


def read_decision_log(dispatch_root: str | Path) -> list[dict[str, Any]]:
    """Read the append-only dashboard decision log if it exists."""
    path = Path(dispatch_root) / "decision_log.jsonl"
    if _has_forbidden_path_part(path) or not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    except OSError:
        return []
    return records


def append_decision_log(
    dispatch_root: str | Path,
    action: ActionInboxItem,
    *,
    decision: str,
    reason: str = "",
    operator: str = "Alberto",
    source: str = "dashboard",
    timestamp: str | None = None,
    prompt_path: str | None = None,
) -> DispatchWriteResult:
    """Append one human-supervised dashboard decision to the Bridge log."""
    target = Path(dispatch_root) / "decision_log.jsonl"
    if _has_forbidden_path_part(target):
        return DispatchWriteResult("REFUSED", warnings=("forbidden_path_name",))
    if decision not in DECISIONS and decision != PROMPT_GENERATED_DECISION:
        return DispatchWriteResult("REFUSED", warnings=(f"unsupported_decision:{decision}",))
    record = {
        "timestamp": timestamp or utc_now(),
        "run_id": action.run_id,
        "action_id": action.action_id,
        "action_key": action.action_key,
        "decision": decision,
        "decision_status": decision_to_status(decision),
        "reason": reason,
        "operator": operator or "Alberto",
        "source": source,
        "human_required": True,
        "no_auto_action": True,
        "prompt_path": prompt_path,
    }
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError as exc:
        return DispatchWriteResult("WARN", warnings=(f"decision_log_write_failed:{exc}",))
    return DispatchWriteResult("PASS", paths=(str(target),))


def generate_prompt_pack(
    dispatch_root: str | Path,
    action: ActionInboxItem,
    *,
    timestamp: str | None = None,
) -> DispatchWriteResult:
    """Write one suggested-only prompt pack Markdown file into the Bridge."""
    if action.decision_status not in PROMPT_ALLOWED_DECISIONS:
        return DispatchWriteResult(
            "REFUSED",
            warnings=("prompt_generation_requires_human_decision",),
        )
    root = Path(dispatch_root) / action.run_id
    if _has_forbidden_path_part(root):
        return DispatchWriteResult("REFUSED", warnings=("forbidden_path_name",))
    stamp = _timestamp_for_filename(timestamp or utc_now())
    project_slug = _slug(action.project_name or "Generic Review").replace("-", "_")
    title_slug = _slug(action.title)
    prompt_path = root / f"1000-Prompt_{project_slug}_{title_slug}_{stamp}.md"
    try:
        root.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(render_prompt_pack(action), encoding="utf-8", newline="\n")
    except OSError as exc:
        return DispatchWriteResult("WARN", warnings=(f"prompt_pack_write_failed:{exc}",))
    return DispatchWriteResult("PASS", paths=(str(prompt_path),))


def render_prompt_pack(action: ActionInboxItem) -> str:
    """Render a copy-ready, suggested-only prompt for a supervised follow-up step."""
    lines = [
        f"# 1000) Prompt Pack - {action.project_name}",
        "",
        "## Contesto",
        "",
        f"- [F] run_id: {action.run_id}.",
        f"- [F] action_id: {action.action_id}.",
        "- [F] prompt_status: suggested_only.",
        "- [F] no_auto_action: true.",
        "",
        "## Fonte Radar",
        "",
        f"- [F] source_item_id: {action.source_item_id}.",
        f"- [F] title: {action.title}.",
        f"- [F] summary: {action.summary}.",
        "",
        "## Progetto Target",
        "",
        f"- [F] project_key: {action.project_key or 'unknown'}.",
        f"- [F] project_name: {action.project_name}.",
        f"- [INT] routing: {'; '.join(action.routing_reasons) or 'NO_DATA'}.",
        "",
        "## Rischio",
        "",
        f"- [F] risk_level: {action.risk_level}.",
        f"- [F] safety_status: {action.safety_status}.",
        f"- [F] human_required: {str(action.human_required).lower()}.",
        "",
        "## Obiettivo",
        "",
        f"- [PROP] {action.recommended_next_step}.",
        "",
        "## Vincoli",
        "",
        "- [F] Non eseguire automaticamente il prompt.",
        "- [F] Non modificare altri repository.",
        "- [F] Non fare commit, push, PR, merge o deploy senza istruzione esplicita.",
        "- [F] Non chiamare LLM o API esterne automaticamente.",
        "- [F] Non inviare email o notifiche automatiche.",
        "- [F] Non modificare scheduler.",
        "",
        "## Cosa Non Fare",
        "",
        *_bullet_lines(action.blocked_outputs, prefix="[F] blocked_output"),
        "",
        "## Test Richiesti",
        "",
        "- [PROP] Eseguire solo test locali pertinenti al progetto target.",
        "- [PROP] Fermarsi e riportare se il progetto target richiede credenziali, rete o dati sensibili.",
        "",
        "## Output Atteso",
        "",
        "- [PROP] Report supervisionato per Alberto con stato, evidenze, rischi e prossimo step.",
        "- [PROP] Nessuna esecuzione automatica.",
        "",
        "## Evidenze",
        "",
        *_bullet_lines(action.evidence_paths, prefix="[F] evidence"),
        "",
        "## Ragioni",
        "",
        *_bullet_lines(action.reasons, prefix="[INT] reason"),
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def export_backlog(
    dispatch_root: str | Path,
    run_id: str,
    actions: list[ActionInboxItem] | tuple[ActionInboxItem, ...],
) -> DispatchWriteResult:
    """Export Markdown and JSON backlog files for one run into the Bridge."""
    root = Path(dispatch_root) / run_id
    if _has_forbidden_path_part(root):
        return DispatchWriteResult("REFUSED", warnings=("forbidden_path_name",))
    markdown_path = root / "1040-Action_Backlog.md"
    json_path = root / "1040-Action_Backlog.json"
    try:
        root.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(
            render_backlog_markdown(run_id, actions),
            encoding="utf-8",
            newline="\n",
        )
        write_json(
            json_path,
            {
                "schema_version": 1,
                "run_id": run_id,
                "actions": [action.to_dict() for action in actions],
                "no_auto_action": True,
            },
        )
    except (OSError, ValueError) as exc:
        return DispatchWriteResult("WARN", warnings=(f"backlog_export_failed:{exc}",))
    return DispatchWriteResult("PASS", paths=(str(markdown_path), str(json_path)))


def render_backlog_markdown(
    run_id: str,
    actions: list[ActionInboxItem] | tuple[ActionInboxItem, ...],
) -> str:
    """Render a readable backlog grouped by priority and decision state."""
    groups = [
        ("High Priority", lambda action: action.priority == "high"),
        ("Medium Priority", lambda action: action.priority == "medium"),
        ("Monitor", lambda action: action.priority == "monitor"),
        ("Backlog", lambda action: action.decision_status == "backlog"),
        ("Ignored", lambda action: action.decision_status == "ignored"),
        ("Deferred", lambda action: action.decision_status == "deferred"),
    ]
    lines = [
        "# 1040) Action Backlog",
        "",
        f"- [F] run_id: {run_id}.",
        "- [F] no_auto_action: true.",
        "",
    ]
    for title, predicate in groups:
        lines.extend([f"## {title}", ""])
        selected = [action for action in actions if predicate(action)]
        if not selected:
            lines.append("- [F] none")
        for action in selected:
            prompt = action.suggested_prompt_path or "not_generated"
            evidence = "; ".join(action.evidence_paths) if action.evidence_paths else "NO_DATA"
            lines.extend(
                [
                    f"### {action.title}",
                    "",
                    f"- [F] project: {action.project_name}.",
                    f"- [F] priority: {action.priority} ({action.priority_score}).",
                    f"- [F] risk: {action.risk_level}.",
                    f"- [F] decision: {action.decision_status}.",
                    f"- [F] recommended_prompt: {prompt}.",
                    f"- [F] evidence: {evidence}.",
                    "",
                ]
            )
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def decision_to_status(decision: str) -> str:
    """Map dashboard button decisions to persisted action statuses."""
    mapping = {
        "approve_prompt": "approved_for_prompt",
        "defer": "deferred",
        "ignore": "ignored",
        "backlog": "backlog",
        "request_review": "review_requested",
        PROMPT_GENERATED_DECISION: "approved_for_prompt",
    }
    return mapping.get(decision, "undecided")


def utc_now() -> str:
    """Return a stable UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _build_action(
    raw: dict[str, Any],
    detail: dict[str, Any],
    *,
    run_id: str,
    timestamp: str,
    previous_keys: set[str],
    record_index: dict[str, dict[str, dict[str, Any]]],
) -> ActionInboxItem:
    run = _mapping(detail.get("run"))
    project_key = _string(raw.get("project_key")) or _project_key_from_name(
        _string(raw.get("target_project")) or _string(raw.get("project_name"))
    )
    project_name = _project_name(project_key, raw)
    source_item_id = (
        _string(raw.get("source_item_id"))
        or _string(raw.get("item_id"))
        or _normalize_title(_string(raw.get("title")) or "radar_action")
    )
    title = _string(raw.get("title")) or "Radar action"
    action_type = _action_type(raw)
    action_key = _action_key(project_key, source_item_id, title)
    action_id = _action_id(run_id, action_key, action_type)
    latest_record = record_index["by_action_id"].get(action_id) or record_index["by_action_key"].get(
        action_key
    )
    decision_status = (
        _string(latest_record.get("decision_status")) if latest_record else None
    ) or "undecided"
    suggested_prompt_path = (
        _string(latest_record.get("prompt_path")) if latest_record else None
    )
    trend_status, trend_reasons = _trend_status(
        action_key=action_key,
        previous_keys=previous_keys,
        latest_record=latest_record,
    )
    priority_score, priority_reasons = _score_priority(
        raw,
        run,
        action_type=action_type,
        trend_status=trend_status,
        decision_status=decision_status,
    )
    priority = _priority(priority_score)
    priority, priority_score, noise_status, noise_reasons = _apply_noise_rules(
        priority=priority,
        priority_score=priority_score,
        raw=raw,
        action_type=action_type,
        trend_status=trend_status,
        decision_status=decision_status,
    )
    safety = _safety(action_type, decision_status, _string(raw.get("triage_class")))
    return ActionInboxItem(
        action_id=action_id,
        action_key=action_key,
        run_id=run_id,
        source_item_id=source_item_id,
        title=title,
        summary=_summary(raw),
        project_key=project_key,
        project_name=project_name,
        action_type=action_type,
        priority=priority,
        priority_score=priority_score,
        risk_level=_string(raw.get("risk_class") or raw.get("risk_level")) or "L1/L2",
        decision_status=decision_status,
        safety_status=safety["safety_status"],
        suggested_prompt_path=suggested_prompt_path,
        created_at=_string(run.get("sort_key")) or timestamp,
        updated_at=timestamp,
        reasons=tuple(_compact_strings([raw.get("reason"), raw.get("triage_class")])),
        evidence_paths=tuple(_evidence_paths(detail)),
        priority_reasons=tuple(priority_reasons),
        routing_reasons=tuple(_routing_reasons(project_key, project_name, raw)),
        recommended_next_step=_recommended_next_step(action_type, project_name, decision_status),
        safety_reasons=tuple(safety["safety_reasons"]),
        allowed_outputs=tuple(safety["allowed_outputs"]),
        blocked_outputs=tuple(safety["blocked_outputs"]),
        trend_status=trend_status,
        trend_reasons=tuple(trend_reasons),
        noise_status=noise_status,
        noise_reasons=tuple(noise_reasons),
        prompt_generation_allowed=safety["prompt_generation_allowed"],
    )


def _raw_actions_from_detail(detail: dict[str, Any], warnings: list[str]) -> list[dict[str, Any]]:
    raw_actions: list[dict[str, Any]] = []
    for key in ("direct_actions", "blocked_actions", "monitor_only_summary"):
        for raw in _list(detail.get(key)):
            if isinstance(raw, dict):
                item = dict(raw)
                item.setdefault("_source_bucket", key)
                raw_actions.append(item)
    for raw in _list(detail.get("manual_review_queue")):
        if isinstance(raw, dict):
            item = {
                "triage_class": "manual_review",
                "title": raw.get("title") or f"Manual review: {raw.get('source_id', 'unknown_source')}",
                "target_project": "Radar source coverage",
                "project_key": "ai_release_radar",
                "reason": raw.get("reason") or "manual review required",
                "risk_class": "L1/L2",
                "severity": raw.get("severity"),
                "_source_bucket": "manual_review_queue",
            }
            raw_actions.append(item)
    if not raw_actions:
        for raw in _list(detail.get("prompt_suggestions")):
            if isinstance(raw, dict):
                item = {
                    "triage_class": "codex_prompt_candidate",
                    "title": raw.get("title") or "Prompt suggestion",
                    "target_project": raw.get("target_project") or "Ambiguous project",
                    "project_key": raw.get("project_key"),
                    "reason": raw.get("reason") or "existing suggested-only prompt",
                    "risk_class": raw.get("risk_class") or "L1/L2",
                    "_source_bucket": "prompt_suggestions",
                }
                raw_actions.append(item)
    if not raw_actions:
        warnings.append("no_action_inbox_candidates")
    return raw_actions


def _previous_action_keys(run_details: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for detail in run_details:
        for raw in _raw_actions_from_detail(detail, []):
            project_key = _string(raw.get("project_key")) or _project_key_from_name(
                _string(raw.get("target_project")) or _string(raw.get("project_name"))
            )
            source_item_id = (
                _string(raw.get("source_item_id"))
                or _string(raw.get("item_id"))
                or _normalize_title(_string(raw.get("title")) or "radar_action")
            )
            keys.add(_action_key(project_key, source_item_id, _string(raw.get("title")) or "Radar action"))
    return keys


def _decision_record_index(records: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    by_action_id: dict[str, dict[str, Any]] = {}
    by_action_key: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        action_id = _string(record.get("action_id"))
        action_key = _string(record.get("action_key"))
        if action_id:
            by_action_id[action_id] = record
        if action_key:
            by_action_key[action_key] = record
    return {"by_action_id": by_action_id, "by_action_key": by_action_key}


def _trend_status(
    *,
    action_key: str,
    previous_keys: set[str],
    latest_record: dict[str, Any] | None,
) -> tuple[str, list[str]]:
    decision_status = _string(latest_record.get("decision_status")) if latest_record else None
    decision = _string(latest_record.get("decision")) if latest_record else None
    prompt_path = _string(latest_record.get("prompt_path")) if latest_record else None
    if prompt_path or decision == PROMPT_GENERATED_DECISION:
        return "prompt_already_generated", ["prompt pack was already generated from dashboard"]
    if decision_status == "backlog":
        return "already_backlogged", ["matching action is already in backlog"]
    if decision_status == "ignored":
        return "previously_ignored", ["matching action was previously ignored"]
    if action_key in previous_keys:
        return "recurring", ["matching source item or normalized title appeared in recent runs"]
    return "new_today", ["not found in recent previous runs"]


def _score_priority(
    raw: dict[str, Any],
    run: dict[str, Any],
    *,
    action_type: str,
    trend_status: str,
    decision_status: str,
) -> tuple[int, list[str]]:
    score = _int(raw.get("score"), default=50)
    reasons = [f"base_score={score}"]
    triage_class = _string(raw.get("triage_class")) or ""
    if action_type == "prepare_prompt" or triage_class == "codex_prompt_candidate":
        score += 20
        reasons.append("direct prompt candidate")
    if action_type == "monitor_only":
        score -= 25
        reasons.append("monitor_only lowers urgency")
    if triage_class in {"blocked_by_coverage", "blocked_by_manual_review", "manual_review"}:
        score += 10
        reasons.append("human gate or coverage review required")
    hag_status = str(run.get("hag_status") or "").upper()
    if hag_status.startswith("HOLD") or "HUMAN" in hag_status:
        score += 5
        reasons.append(f"HAG status requires attention: {hag_status}")
    risk = str(raw.get("risk_class") or "")
    if "L4" in risk:
        score -= 20
        reasons.append("sensitive target reduces dispatch priority")
    elif "L2" in risk:
        score += 5
        reasons.append("L2 review risk visible")
    if trend_status == "recurring":
        score += 10
        reasons.append("recurring multi-day signal")
    if trend_status == "new_today":
        score += 5
        reasons.append("new today")
    source_count = _int(run.get("source_count"), default=0)
    parsed_count = _int(run.get("parsed_count"), default=0)
    if source_count and parsed_count / source_count >= 0.50:
        score += 5
        reasons.append("source confidence >= 50 percent parsed")
    else:
        score -= 5
        reasons.append("source confidence below 50 percent or unavailable")
    if decision_status in {"ignored", "backlog", "deferred"}:
        score -= 30
        reasons.append(f"existing decision lowers urgency: {decision_status}")
    return max(0, min(100, score)), reasons


def _priority(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 55:
        return "medium"
    if score >= 35:
        return "low"
    return "monitor"


def _apply_noise_rules(
    *,
    priority: str,
    priority_score: int,
    raw: dict[str, Any],
    action_type: str,
    trend_status: str,
    decision_status: str,
) -> tuple[str, int, str, list[str]]:
    reasons: list[str] = []
    noise_status = "visible"
    title = _normalize_title(_string(raw.get("title")) or "")
    if decision_status == "ignored" or trend_status == "previously_ignored":
        priority = "monitor"
        priority_score = min(priority_score, 30)
        noise_status = "suppressed"
        reasons.append("previously ignored actions cannot stay high priority")
    elif decision_status == "backlog" or trend_status == "already_backlogged":
        priority = "monitor"
        priority_score = min(priority_score, 35)
        noise_status = "suppressed"
        reasons.append("already backlogged actions are shown without escalation")
    elif action_type == "monitor_only" and trend_status == "recurring" and priority_score < 55:
        priority = "monitor"
        noise_status = "downgraded"
        reasons.append("recurring low-score monitor-only action remains monitor")
    elif "patch" in title and trend_status == "recurring":
        priority_score = min(priority_score, 54)
        priority = _priority(priority_score)
        noise_status = "downgraded"
        reasons.append("recurring patch release already seen lowers priority")
    return priority, priority_score, noise_status, reasons


def _safety(
    action_type: str,
    decision_status: str,
    triage_class: str | None,
) -> dict[str, Any]:
    blocked_outputs = [
        "auto_action",
        "external_repo_write",
        "llm_call",
        "email",
        "scheduler_change",
    ]
    allowed_outputs = ["bridge_decision_log", "bridge_backlog_export"]
    prompt_allowed = decision_status in PROMPT_ALLOWED_DECISIONS
    if prompt_allowed:
        allowed_outputs.append("bridge_prompt_markdown")
    reasons = [
        "auto_action_allowed=false",
        "external_repo_write_allowed=false",
        "llm_call_allowed=false",
        "email_allowed=false",
        "scheduler_change_allowed=false",
    ]
    if triage_class in {"blocked_by_coverage", "blocked_by_manual_review"}:
        safety_status = "blocked_auto_action"
        reasons.append("candidate is blocked for automatic action")
    elif prompt_allowed or action_type in {"monitor_only", "no_action"}:
        safety_status = "safe_prompt_only"
        reasons.append("only Bridge outputs are allowed")
    else:
        safety_status = "requires_human_approval"
        reasons.append("prompt generation requires explicit human decision")
    return {
        "safety_status": safety_status,
        "safety_reasons": reasons,
        "allowed_outputs": allowed_outputs,
        "blocked_outputs": blocked_outputs,
        "prompt_generation_allowed": prompt_allowed,
    }


def _action_type(raw: dict[str, Any]) -> str:
    action_type = _string(raw.get("action_type"))
    if action_type in ACTION_TYPES:
        return action_type
    triage_class = _string(raw.get("triage_class"))
    if triage_class == "monitor":
        return "monitor_only"
    if triage_class == "ignore":
        return "no_action"
    if triage_class == "codex_prompt_candidate":
        return "prepare_prompt"
    if triage_class == "blocked_by_coverage":
        return "review_release"
    if triage_class in {"blocked_by_manual_review", "manual_review"}:
        return "check_compatibility"
    return "review_release"


def _summary(raw: dict[str, Any]) -> str:
    values = _compact_strings(
        [
            raw.get("summary"),
            raw.get("reason"),
            raw.get("severity"),
            raw.get("item_category"),
        ]
    )
    return "; ".join(values) if values else "Radar action candidate"


def _routing_reasons(
    project_key: str | None,
    project_name: str,
    raw: dict[str, Any],
) -> list[str]:
    reasons = []
    if project_key:
        reasons.append(f"project_key={project_key}")
    reasons.append(f"project_name={project_name}")
    reason = _string(raw.get("reason"))
    if reason:
        reasons.append(reason)
    return reasons


def _recommended_next_step(
    action_type: str,
    project_name: str,
    decision_status: str,
) -> str:
    if decision_status == "backlog":
        return f"Keep {project_name} item in backlog until Alberto schedules it."
    if decision_status == "ignored":
        return f"Keep {project_name} item visible as ignored evidence."
    if action_type == "monitor_only":
        return f"Monitor {project_name}; do not create implementation work."
    if action_type == "prepare_prompt":
        return f"Prepare a supervised prompt pack for {project_name} after approval."
    return f"Review {project_name} impact and decide whether to generate a prompt pack."


def _evidence_paths(detail: dict[str, Any]) -> list[str]:
    run = _mapping(detail.get("run"))
    files = _mapping(run.get("files"))
    preferred = [
        "action_triage_json",
        "prompt_suggestions_markdown",
        "hag_report_markdown",
        "dashboard_path",
        "daily_sim_summary",
    ]
    paths = [str(files[key]) for key in preferred if isinstance(files.get(key), str)]
    run_dir = _string(run.get("run_dir"))
    if run_dir:
        paths.append(run_dir)
    return sorted(set(paths))


def _project_name(project_key: str | None, raw: dict[str, Any]) -> str:
    explicit = _string(raw.get("project_name") or raw.get("target_project"))
    if explicit and explicit != "Ambiguous project":
        return explicit
    lookup = {
        "ai_software_factory": "AI Software Factory",
        "codex_skills": "Codex_Skills",
        "family_photo_organizer": "Family Photo Organizer",
        "mansionario_vivo": "Mansionario_Vivo",
        "agglodetect": "AggloDetect",
        "diamsign": "DiamSign",
        "controllo_gestione_esolver": "ControlloGestioneExcel / eSolver",
        "ai_release_radar": "AI Release Radar",
    }
    return lookup.get(project_key or "", explicit or "Ambiguous project")


def _project_key_from_name(name: str | None) -> str | None:
    if not name:
        return None
    normalized = _normalize_title(name)
    mapping = {
        "ai-software-factory": "ai_software_factory",
        "codex-skills": "codex_skills",
        "codex-skills": "codex_skills",
        "family-photo-organizer": "family_photo_organizer",
        "mansionario-vivo": "mansionario_vivo",
        "agglodetect": "agglodetect",
        "diamsign": "diamsign",
        "controllogestioneexcel-esolver": "controllo_gestione_esolver",
        "radar-source-coverage": "ai_release_radar",
        "ai-release-radar": "ai_release_radar",
    }
    return mapping.get(normalized)


def _action_key(project_key: str | None, source_item_id: str, title: str) -> str:
    return f"{project_key or 'unknown'}:{source_item_id or _normalize_title(title)}"


def _action_id(run_id: str, action_key: str, action_type: str) -> str:
    digest = hashlib.sha256(f"{run_id}|{action_key}|{action_type}".encode("utf-8")).hexdigest()
    return f"act_{digest[:12]}"


def _priority_rank(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2, "monitor": 3}.get(priority, 4)


def _bullet_lines(values: tuple[str, ...] | list[str], *, prefix: str) -> list[str]:
    if not values:
        return [f"- {prefix}: none."]
    return [f"- {prefix}: {value}." for value in values]


def _compact_strings(values: list[Any]) -> list[str]:
    result = []
    for value in values:
        text = _string(value)
        if text and text not in result:
            result.append(text)
    return result


def _normalize_title(value: str) -> str:
    return _slug(value)


def _slug(value: str) -> str:
    text = value.strip().lower().replace("_", "-")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "radar-action"


def _timestamp_for_filename(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z]+", "", value)[:15] or "00000000T000000"


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _int(value: Any, *, default: int) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return default


def _has_forbidden_path_part(path: Path) -> bool:
    return any(part.startswith(FORBIDDEN_PREFIXES) for part in path.parts)

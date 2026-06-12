"""Action Center orchestration for the local dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from radar.action_inbox import (
    DECISIONS,
    ActionInbox,
    ActionInboxItem,
    append_decision_log,
    build_action_inbox,
    export_backlog,
    generate_prompt_pack,
    read_decision_log,
)
from radar_web.config import DashboardConfig
from radar_web.run_locator import list_recent_runs, load_run_detail


ACTION_DISPATCH_DIR = "action_dispatch"
ACTION_FILTERS = ("all", "high", "medium", "monitor", "undecided", "backlog")


def dispatch_root(config: DashboardConfig) -> Path:
    """Return the Bridge action dispatch root."""
    return config.bridge_root / ACTION_DISPATCH_DIR


def build_action_center_payload(
    config: DashboardConfig,
    *,
    filter_value: str = "all",
    limit: int = 10,
) -> dict[str, Any]:
    """Build the dashboard/API payload for the supervised Action Center."""
    bounded_limit = max(1, min(limit, 50))
    root = dispatch_root(config)
    warnings = list(config.validate_output_root(root))
    details = _load_recent_details(config, bounded_limit, warnings)
    records = read_decision_log(root)
    inbox = build_action_inbox(details, decision_records=records)
    actions = list(inbox.actions)
    selected_filter = filter_value if filter_value in ACTION_FILTERS else "all"
    filtered = _filter_actions(actions, selected_filter)
    scope = _run_scope_context(root, inbox.run_id, details, records)
    warnings.extend(scope["warnings"])
    return {
        "schema_version": 1,
        "run_id": inbox.run_id,
        "dispatch_root": str(root),
        "current_run_dispatch_root": scope["current_run_dispatch_root"],
        "current_run_dispatch_exists": scope["current_run_dispatch_exists"],
        "decision_run_ids": scope["decision_run_ids"],
        "current_run_decision_count": scope["current_run_decision_count"],
        "historical_decision_count": scope["historical_decision_count"],
        "showing_historical_decisions": scope["showing_historical_decisions"],
        "run_output_has_hag": scope["run_output_has_hag"],
        "current_hag_status": scope["current_hag_status"],
        "run_output_has_prompt_suggestions": scope["run_output_has_prompt_suggestions"],
        "run_output_has_action_triage": scope["run_output_has_action_triage"],
        "run_scope_status": scope["run_scope_status"],
        "run_scope_message": scope["run_scope_message"],
        "filters": list(ACTION_FILTERS),
        "selected_filter": selected_filter,
        "actions": [action.to_dict() for action in filtered],
        "all_actions": [action.to_dict() for action in actions],
        "actions_count": len(filtered),
        "all_actions_count": len(actions),
        "decision_log_path": str(root / "decision_log.jsonl"),
        "warnings": sorted(set(warnings).union(inbox.warnings)),
        "no_auto_action": True,
    }


def get_action(config: DashboardConfig, action_id: str) -> ActionInboxItem | None:
    """Return one action candidate from the current inbox."""
    inbox = _build_current_inbox(config)
    for action in inbox.actions:
        if action.action_id == action_id:
            return action
    return None


def record_decision(
    config: DashboardConfig,
    action_id: str,
    *,
    decision: str,
    reason: str = "",
    operator: str = "Alberto",
) -> dict[str, Any]:
    """Persist one human dashboard decision in the Bridge decision log."""
    if decision not in DECISIONS:
        return {
            "status": "REFUSED",
            "message": f"unsupported decision: {decision}",
            "warnings": [f"unsupported_decision:{decision}"],
            "no_auto_action": True,
        }
    action = get_action(config, action_id)
    if action is None:
        return {
            "status": "NO_DATA",
            "message": f"Action not found: {action_id}",
            "warnings": ["action_not_found"],
            "no_auto_action": True,
        }
    warnings = _write_warnings(config)
    if warnings:
        return {
            "status": "REFUSED",
            "message": "Action dispatch root is not safe for writes.",
            "warnings": warnings,
            "no_auto_action": True,
        }
    result = append_decision_log(
        dispatch_root(config),
        action,
        decision=decision,
        reason=reason,
        operator=operator,
    )
    return {
        "status": result.status,
        "action": action.to_dict(),
        "decision": decision,
        "human_required": True,
        "paths": list(result.paths),
        "warnings": list(result.warnings),
        "no_auto_action": True,
    }


def generate_prompt_for_action(config: DashboardConfig, action_id: str) -> dict[str, Any]:
    """Generate a Bridge-only Markdown prompt pack after a human decision."""
    action = get_action(config, action_id)
    if action is None:
        return {
            "status": "NO_DATA",
            "message": f"Action not found: {action_id}",
            "warnings": ["action_not_found"],
            "no_auto_action": True,
        }
    warnings = _write_warnings(config)
    if warnings:
        return {
            "status": "REFUSED",
            "message": "Action dispatch root is not safe for writes.",
            "warnings": warnings,
            "no_auto_action": True,
        }
    result = generate_prompt_pack(dispatch_root(config), action)
    if result.status == "PASS" and result.paths:
        append_decision_log(
            dispatch_root(config),
            action,
            decision="prompt_generated",
            reason="prompt pack generated by explicit dashboard request",
            prompt_path=result.paths[0],
        )
    return {
        "status": result.status,
        "action": action.to_dict(),
        "paths": list(result.paths),
        "warnings": list(result.warnings),
        "human_required": True,
        "no_auto_action": True,
        "prompt_executed": False,
    }


def export_current_backlog(config: DashboardConfig) -> dict[str, Any]:
    """Export the current action backlog into the Bridge."""
    inbox = _build_current_inbox(config)
    if inbox.run_id is None:
        return {
            "status": "NO_DATA",
            "message": "No run available for backlog export.",
            "warnings": list(inbox.warnings),
            "no_auto_action": True,
        }
    warnings = _write_warnings(config)
    if warnings:
        return {
            "status": "REFUSED",
            "message": "Action dispatch root is not safe for writes.",
            "warnings": warnings,
            "no_auto_action": True,
        }
    result = export_backlog(dispatch_root(config), inbox.run_id, inbox.actions)
    return {
        "status": result.status,
        "run_id": inbox.run_id,
        "paths": list(result.paths),
        "warnings": list(result.warnings),
        "no_auto_action": True,
    }


def _build_current_inbox(config: DashboardConfig) -> ActionInbox:
    warnings: list[str] = []
    details = _load_recent_details(config, 10, warnings)
    return build_action_inbox(details, decision_records=read_decision_log(dispatch_root(config)))


def _load_recent_details(
    config: DashboardConfig,
    limit: int,
    warnings: list[str],
) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    runs = list_recent_runs(config.runs_root, limit=limit)
    for run in runs:
        detail = load_run_detail(config.runs_root, run.run_id)
        if detail is None:
            warnings.append(f"run_detail_missing:{run.run_id}")
            continue
        details.append(detail)
    if not details:
        warnings.append("no_recent_run_details")
    return details


def _filter_actions(actions: list[ActionInboxItem], filter_value: str) -> list[ActionInboxItem]:
    if filter_value == "all":
        return actions
    if filter_value in {"high", "medium", "monitor"}:
        return [action for action in actions if action.priority == filter_value]
    if filter_value == "undecided":
        return [action for action in actions if action.decision_status == "undecided"]
    if filter_value == "backlog":
        return [action for action in actions if action.decision_status == "backlog"]
    return actions


def _run_scope_context(
    root: Path,
    run_id: str | None,
    details: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    current_dispatch_root = root / run_id if run_id else root
    decision_run_ids = sorted(
        {
            str(record.get("run_id"))
            for record in records
            if isinstance(record, dict) and str(record.get("run_id") or "").strip()
        }
    )
    current_records = [
        record
        for record in records
        if isinstance(record, dict) and str(record.get("run_id") or "") == str(run_id or "")
    ]
    historical_records = [
        record
        for record in records
        if isinstance(record, dict) and str(record.get("run_id") or "") != str(run_id or "")
    ]
    latest_detail = details[0] if details else {}
    latest_run = _mapping(latest_detail.get("run"))
    run_files = _mapping(latest_run.get("files"))
    prompt_suggestions = latest_detail.get("prompt_suggestions")
    prompt_count = len(prompt_suggestions) if isinstance(prompt_suggestions, list) else 0
    context = {
        "current_run_dispatch_root": str(current_dispatch_root),
        "current_run_dispatch_exists": current_dispatch_root.is_dir(),
        "decision_run_ids": decision_run_ids,
        "current_run_decision_count": len(current_records),
        "historical_decision_count": len(historical_records),
        "showing_historical_decisions": bool(historical_records),
        "run_output_has_hag": bool(run_files.get("hag_report_markdown")),
        "current_hag_status": str(latest_run.get("hag_status") or "NO_DATA"),
        "run_output_has_prompt_suggestions": bool(run_files.get("prompt_suggestions_markdown"))
        or prompt_count > 0,
        "run_output_has_action_triage": bool(run_files.get("action_triage_json")),
        "warnings": [],
    }
    if run_id is None:
        context["run_scope_status"] = "NO_DATA"
        context["run_scope_message"] = "No current run is available for Action Center scope."
        context["warnings"].append("action_center_current_run_missing")
    elif not context["current_run_dispatch_exists"] and (
        context["run_output_has_hag"] or context["run_output_has_prompt_suggestions"]
    ):
        context["run_scope_status"] = "RUN_OUTPUT_ONLY"
        context["run_scope_message"] = (
            "Current run has HAG or prompt suggestions in run output, but no "
            "action_dispatch folder exists for this run."
        )
        context["warnings"].append("current_run_action_dispatch_missing_run_output_available")
    else:
        context["run_scope_status"] = "RUN_SCOPED"
        context["run_scope_message"] = "Action Center is scoped to the current run."
    if historical_records:
        context["warnings"].append("historical_action_dispatch_decisions_present")
    return context


def _write_warnings(config: DashboardConfig) -> list[str]:
    root = dispatch_root(config)
    return sorted(set(config.validate_output_root(root)))


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

"""Bridge-only Daily Review Pack generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from radar.json_utils import read_json, write_json
from radar.source_coverage import (
    build_source_coverage_matrix,
    render_source_coverage_matrix_markdown,
    summarize_source_coverage_matrix,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = ("LAST-", "latest-")
DAILY_REVIEW_PACK_JSON = "1390-Daily_Review_Pack.json"
DAILY_REVIEW_PACK_MARKDOWN = "1390-Daily_Review_Pack.md"


def build_daily_review_pack(
    run_dir: str | Path,
    *,
    scheduler_log_path: str | Path | None = None,
) -> dict[str, object]:
    """Build a deterministic operator review pack from an existing run directory."""
    root = Path(run_dir).expanduser().resolve()
    run_summary = _read_json_if_present(root / "0180-Run_Summary.json")
    daily_summary = _read_json_if_present(root / "0350-Daily_Sim_Summary.json")
    quality_gate = _read_json_if_present(root / "0630-Daily_Quality_Gate_V2.json")
    action_triage = _read_json_if_present(root / "0650-Action_Triage.json")
    prompt_suggestions = _read_json_if_present(root / "0660-Codex_Prompt_Suggestions.json")
    result = _real_run(run_summary, daily_summary)
    source_matrix = build_source_coverage_matrix(result.get("source_diagnostics"))
    source_summary = summarize_source_coverage_matrix(source_matrix)
    scheduler_evidence = parse_scheduler_log(scheduler_log_path) if scheduler_log_path else {}
    safety = {
        "no_auto_action": _falsey(daily_summary.get("auto_action_executed")),
        "no_email": _falsey(daily_summary.get("email_sent")),
        "no_runtime_llm": _falsey(daily_summary.get("llm_called")),
        "no_external_notification": True,
        "no_scheduler_mutation": _falsey(daily_summary.get("scheduler_activated")),
    }
    pack = {
        "schema_version": 1,
        "pack_type": "daily_review_pack",
        "run_id": root.name,
        "radar_run_id": result.get("run_id"),
        "run_dir": str(root),
        "status": daily_summary.get("status") or result.get("status") or "NO_DATA",
        "scheduler_status": _scheduler_status(scheduler_evidence, daily_summary),
        "gate_status": daily_summary.get("automation_gate_status") or "NO_DATA",
        "daily_quality_gate_status": quality_gate.get("overall_daily_review_status") or "NO_DATA",
        "source_coverage_status": quality_gate.get("source_coverage_status") or "NO_DATA",
        "hag_status": daily_summary.get("hag_status") or "NO_DATA",
        "readiness": _pack_readiness(quality_gate, daily_summary),
        "recommendation": (
            daily_summary.get("recommendation")
            or "Manual review required before acting; no auto-action."
        ),
        "safety_summary": safety,
        "source_coverage_summary": source_summary,
        "source_coverage_matrix": source_matrix,
        "manual_review_sources": _sources_by_flag(source_matrix, "manual_review_required", True),
        "unsupported_sources_explained": _sources_by_status(
            source_matrix,
            "fetched_but_unsupported",
        ),
        "action_summary": _action_summary(result, action_triage, daily_summary),
        "hag_summary": _hag_summary(daily_summary, action_triage, prompt_suggestions),
        "prompt_suggestions_summary": _prompt_summary(prompt_suggestions, root.name),
        "operator_checklist": _operator_checklist(),
        "maintenance_backlog_pointers": _maintenance_backlog_pointers(source_matrix),
        "scheduler_evidence": scheduler_evidence,
        "warnings": _warnings(source_summary, quality_gate, action_triage, prompt_suggestions),
    }
    return pack


def write_daily_review_pack(
    run_dir: str | Path,
    output_dir: str | Path,
    *,
    scheduler_log_path: str | Path | None = None,
) -> dict[str, str]:
    """Write the review pack JSON and Markdown to an explicit outside-repo directory."""
    target_dir = _outside_repo_output_dir(output_dir)
    pack = build_daily_review_pack(run_dir, scheduler_log_path=scheduler_log_path)
    json_path = target_dir / DAILY_REVIEW_PACK_JSON
    markdown_path = target_dir / DAILY_REVIEW_PACK_MARKDOWN
    write_json(json_path, pack)
    markdown_path.write_text(render_daily_review_pack_markdown(pack), encoding="utf-8", newline="\n")
    return {
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "run_id": str(pack.get("run_id") or ""),
        "status": str(pack.get("readiness") or "NO_DATA"),
    }


def render_daily_review_pack_markdown(pack: dict[str, object]) -> str:
    """Render a human-readable Daily Review Pack."""
    source_summary = _mapping(pack.get("source_coverage_summary"))
    action_summary = _mapping(pack.get("action_summary"))
    hag_summary = _mapping(pack.get("hag_summary"))
    prompt_summary = _mapping(pack.get("prompt_suggestions_summary"))
    scheduler = _mapping(pack.get("scheduler_evidence"))
    safety = _mapping(pack.get("safety_summary"))
    lines = [
        "# 1390) Daily Review Pack",
        "",
        "## 1. Executive Summary",
        "",
        f"- [F] run_dir: {pack.get('run_dir')}.",
        f"- [F] radar_run_id: {pack.get('radar_run_id')}.",
        f"- [F] status: {pack.get('status')}.",
        f"- [F] scheduler_status: {pack.get('scheduler_status')}.",
        f"- [F] gate_status: {pack.get('gate_status')}.",
        f"- [F] daily_quality_gate_status: {pack.get('daily_quality_gate_status')}.",
        f"- [F] HAG status: {pack.get('hag_status')}.",
        f"- [F] readiness: {pack.get('readiness')}.",
        f"- [PROP] recommendation: {pack.get('recommendation')}.",
        "",
        "## 2. Safety Summary",
        "",
        f"- [F] no_auto_action: {str(safety.get('no_auto_action')).lower()}.",
        f"- [F] no_email: {str(safety.get('no_email')).lower()}.",
        f"- [F] no_runtime_llm: {str(safety.get('no_runtime_llm')).lower()}.",
        f"- [F] no_external_notification: {str(safety.get('no_external_notification')).lower()}.",
        f"- [F] no_scheduler_mutation: {str(safety.get('no_scheduler_mutation')).lower()}.",
        "",
        "## 3. Source Coverage Summary",
        "",
        f"- [F] fonti_totali: {source_summary.get('source_count')}.",
        f"- [F] fonti_parsate: {source_summary.get('parsed_count')}.",
        f"- [F] fonti_unsupported: {source_summary.get('unsupported_source_count')}.",
        f"- [F] fonti_manual_review: {source_summary.get('manual_review_required_count')}.",
        f"- [F] fonti_fallite: {source_summary.get('failed_count')}.",
        f"- [F] coverage_warning: {str(source_summary.get('coverage_warning')).lower()}.",
        "",
        "## 4. Source Coverage Final Matrix",
        "",
        render_source_coverage_matrix_markdown(pack.get("source_coverage_matrix")),
        "",
        "## 5. Manual Review Queue",
        "",
    ]
    manual_review_sources = _list(pack.get("manual_review_sources"))
    if manual_review_sources:
        for raw in manual_review_sources:
            source = _mapping(raw)
            lines.append(
                "- [F] "
                f"{source.get('source_id')}: "
                f"{source.get('final_v1_status')} - {source.get('final_v1_reason')}"
            )
    else:
        lines.append("- [F] none")
    lines.extend(
        [
            "",
            "## 6. Unsupported Sources Explained",
            "",
        ]
    )
    unsupported_sources = _list(pack.get("unsupported_sources_explained"))
    if unsupported_sources:
        for raw in unsupported_sources:
            source = _mapping(raw)
            lines.append(
                "- [F] "
                f"{source.get('source_id')}: "
                f"{source.get('unsupported_reason')} - {source.get('final_v1_reason')}"
            )
    else:
        lines.append("- [F] none")
    lines.extend(
        [
            "",
            "## 7. Action Summary",
            "",
            f"- [F] direct_actions: {action_summary.get('direct_actions')}.",
            f"- [F] monitor_only_actions: {action_summary.get('monitor_only_actions')}.",
            f"- [F] manual_review_queue: {action_summary.get('manual_review_queue')}.",
            f"- [F] no_action_count: {action_summary.get('no_action_count')}.",
            f"- [F] HOLD reason: {action_summary.get('hold_reason')}.",
            "",
            "## 8. HAG Summary",
            "",
            f"- [F] requires_human_approval: {str(hag_summary.get('requires_human_approval')).lower()}.",
            f"- [F] not_done: {hag_summary.get('not_done')}.",
            f"- [PROP] next_safe_step: {hag_summary.get('next_safe_step')}.",
            "",
            "## 9. Prompt Suggestions Summary",
            "",
            f"- [F] status: {prompt_summary.get('status')}.",
            f"- [F] suggestions_count: {prompt_summary.get('suggestions_count')}.",
            "- [F] prompts_executed: false.",
        ]
    )
    for suggestion in _list(prompt_summary.get("suggestions")):
        if isinstance(suggestion, dict):
            lines.extend(
                [
                    "",
                    f"### {suggestion.get('suggested_step_number')} - {suggestion.get('title')}",
                    "",
                    f"- [F] target_project: {suggestion.get('target_project')}.",
                    f"- [F] risk_class: {suggestion.get('risk_class')}.",
                    f"- [F] manual_only: {str(suggestion.get('manual_only')).lower()}.",
                    f"- [INT] purpose: {suggestion.get('reason')}.",
                ]
            )
    lines.extend(
        [
            "",
            "## 10. Scheduler Evidence",
            "",
            f"- [F] scheduler_log_path: {scheduler.get('log_path', 'NO_DATA')}.",
            f"- [F] command_exit_code: {scheduler.get('command_exit_code', 'NO_DATA')}.",
            f"- [F] daily_sim_exit_code: {scheduler.get('daily_sim_exit_code', 'NO_DATA')}.",
            f"- [F] script_exit_code: {scheduler.get('script_exit_code', 'NO_DATA')}.",
            f"- [F] stderr_path: {scheduler.get('stderr_path', 'NO_DATA')}.",
            f"- [F] no_auto_action_confirmed: {str(scheduler.get('no_auto_action_confirmed', False)).lower()}.",
            "",
            "## 11. Operator Checklist",
            "",
        ]
    )
    lines.extend(f"- [PROP] {item}" for item in _list(pack.get("operator_checklist")))
    lines.extend(["", "## 12. Maintenance Backlog Pointers", ""])
    for item in _list(pack.get("maintenance_backlog_pointers")):
        lines.append(f"- [PROP] {item}")
    lines.extend(["", "## 13. Warnings", ""])
    warnings = _list(pack.get("warnings"))
    if warnings:
        lines.extend(f"- [F] {warning}" for warning in warnings)
    else:
        lines.append("- [F] none")
    return "\n".join(lines).rstrip("\n") + "\n"


def parse_scheduler_log(path: str | Path | None) -> dict[str, object]:
    """Parse scheduler dry-report key evidence from an existing log file."""
    if path is None:
        return {}
    target = Path(path).expanduser().resolve()
    evidence: dict[str, object] = {"log_path": str(target), "exists": target.is_file()}
    if _has_forbidden_path_part(target) or not target.is_file():
        return evidence
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        evidence["warnings"] = [f"scheduler_log_read_failed:{exc}"]
        return evidence
    stdout_lines: list[str] = []
    confirmations = {
        "no_auto_action_confirmed": False,
        "no_email_confirmed": False,
        "no_external_notification_confirmed": False,
        "no_llm_confirmed": False,
        "no_git_commit_push_confirmed": False,
    }
    for line in lines:
        _, _, payload = line.partition(" ")
        key, sep, value = payload.partition("=")
        if sep:
            key = key.strip()
            value = value.strip()
            if key == "stdout":
                stdout_lines.append(value)
            elif key in {
                "command_exit_code",
                "daily_sim_exit_code",
                "script_exit_code",
                "duration_seconds",
                "stderr_path",
                "stdout_path",
                "lock_path",
                "lock_removed",
                "script_exit_reason",
            }:
                evidence[key] = _coerce_log_value(value)
            elif key == "no_auto_action" and value == "confirmed":
                confirmations["no_auto_action_confirmed"] = True
            elif key == "no_email" and value == "confirmed":
                confirmations["no_email_confirmed"] = True
            elif key == "no_external_notification" and value == "confirmed":
                confirmations["no_external_notification_confirmed"] = True
            elif key == "no_llm" and value == "confirmed":
                confirmations["no_llm_confirmed"] = True
            elif key == "no_git_commit_push" and value == "confirmed":
                confirmations["no_git_commit_push_confirmed"] = True
    evidence.update(confirmations)
    evidence["stdout_lines"] = stdout_lines
    return evidence


def _read_json_if_present(path: Path) -> dict[str, Any]:
    if _has_forbidden_path_part(path) or not path.is_file():
        return {}
    data = read_json(path)
    return data if isinstance(data, dict) else {}


def _real_run(run_summary: dict[str, Any], daily_summary: dict[str, Any]) -> dict[str, Any]:
    result = run_summary.get("result")
    if isinstance(result, dict):
        return result
    result = daily_summary.get("real_run")
    return result if isinstance(result, dict) else {}


def _action_summary(
    result: dict[str, Any],
    action_triage: dict[str, Any],
    daily_summary: dict[str, Any],
) -> dict[str, object]:
    counts = _mapping(action_triage.get("counts"))
    return {
        "direct_actions": _int(result.get("direct_action_count")),
        "monitor_only_actions": _int(result.get("monitor_only_action_count")),
        "manual_review_queue": _int(daily_summary.get("manual_review_queue_count")),
        "no_action_count": _int(result.get("no_action_count")),
        "blocked_by_coverage": _int(counts.get("blocked_by_coverage")),
        "manual_review": _int(counts.get("manual_review")),
        "hold_reason": "human approval required before acting on direct actions",
    }


def _hag_summary(
    daily_summary: dict[str, Any],
    action_triage: dict[str, Any],
    prompt_suggestions: dict[str, Any],
) -> dict[str, object]:
    hag_status = str(daily_summary.get("hag_status") or "NO_DATA")
    return {
        "status": hag_status,
        "requires_human_approval": "HOLD" in hag_status or "HUMAN" in hag_status,
        "not_done": "No prompt suggestion, email, LLM call, scheduler change or external action was executed.",
        "next_safe_step": "Alberto reviews one HAG decision and approves at most one separate follow-up step.",
        "action_triage_status": action_triage.get("status") or "NO_DATA",
        "prompt_suggestions_status": prompt_suggestions.get("status") or "NO_DATA",
    }


def _prompt_summary(prompt_suggestions: dict[str, Any], run_id: str) -> dict[str, object]:
    suggestions = []
    for raw in _list(prompt_suggestions.get("suggestions")):
        if isinstance(raw, dict):
            suggestion = dict(raw)
            suggestion["run_id"] = run_id
            suggestion["manual_only"] = True
            suggestion["executed"] = False
            suggestions.append(suggestion)
    return {
        "status": prompt_suggestions.get("status") or "NO_DATA",
        "suggestions_count": _int(prompt_suggestions.get("suggestions_count")),
        "suggestions": suggestions,
        "prompts_executed": False,
    }


def _operator_checklist() -> list[str]:
    return [
        "Aprire dashboard e Action Center sul run corrente.",
        "Leggere HAG e coda di revisione manuale prima di qualunque decisione.",
        "Verificare che le fonti non parsate siano diagnosticate e classificate.",
        "Non eseguire prompt suggestions automaticamente.",
        "Non inviare email, notifiche o chiamate LLM da questo radar.",
        "Selezionare al massimo un follow-up supervisionato come step separato.",
    ]


def _sources_by_flag(matrix: object, field_name: str, expected: object) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in _list(matrix)
        if isinstance(row, dict) and row.get(field_name) == expected
    ]


def _sources_by_status(matrix: object, diagnostic_status: str) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in _list(matrix)
        if isinstance(row, dict) and row.get("diagnostic_status") == diagnostic_status
    ]


def _maintenance_backlog_pointers(matrix: object) -> list[str]:
    pointers: list[str] = []
    for raw in _list(matrix):
        if not isinstance(raw, dict):
            continue
        category = str(raw.get("maintenance_backlog_category") or "none")
        if category == "none":
            continue
        pointers.append(
            f"{raw.get('source_id')}: {category}; follow_up={raw.get('recommended_follow_up')}"
        )
    return sorted(set(pointers))


def _warnings(
    source_summary: dict[str, object],
    quality_gate: dict[str, Any],
    action_triage: dict[str, Any],
    prompt_suggestions: dict[str, Any],
) -> list[str]:
    warnings = [str(item) for item in _list(quality_gate.get("warnings"))]
    if source_summary.get("coverage_warning") is True:
        warnings.append(
            "low_source_coverage:"
            f"{source_summary.get('parsed_count')}/{source_summary.get('source_count')}"
        )
    if int(source_summary.get("manual_review_required_count") or 0) > 0:
        warnings.append("manual_review_sources_present")
    if int(source_summary.get("unsupported_source_count") or 0) > 0:
        warnings.append("unsupported_sources_present")
    if action_triage.get("status") == "HOLD":
        warnings.append("action_triage_hold")
    if prompt_suggestions.get("warnings"):
        warnings.extend(str(item) for item in _list(prompt_suggestions.get("warnings")))
    return sorted(set(warnings))


def _pack_readiness(quality_gate: dict[str, Any], daily_summary: dict[str, Any]) -> str:
    status = str(quality_gate.get("overall_daily_review_status") or "")
    hag_status = str(daily_summary.get("hag_status") or "")
    if status == "FAIL":
        return "BLOCKED"
    if "HOLD" in hag_status or "HUMAN" in hag_status or status == "ACTION_REVIEW_REQUIRED":
        return "READY_FOR_SUPERVISED_HUMAN_REVIEW_WITH_WARNINGS"
    if status in {"WARN", "HOLD"}:
        return "READY_FOR_SUPERVISED_HUMAN_REVIEW_WITH_WARNINGS"
    return "READY_FOR_SUPERVISED_HUMAN_REVIEW"


def _scheduler_status(
    scheduler_evidence: dict[str, object],
    daily_summary: dict[str, Any],
) -> str:
    if scheduler_evidence.get("script_exit_code") == 0:
        return "PASS"
    if scheduler_evidence:
        return "WARNING"
    return str(daily_summary.get("scheduler_readiness_recommendation") or "NO_DATA")


def _outside_repo_output_dir(output_dir: str | Path) -> Path:
    target = Path(output_dir).expanduser().resolve()
    if _is_path_within(target, REPO_ROOT):
        raise ValueError("daily review pack output_dir must be outside repository.")
    if _has_forbidden_path_part(target):
        raise ValueError("daily review pack output_dir must not use LAST-* or latest-* names.")
    target.mkdir(parents=True, exist_ok=True)
    return target


def _has_forbidden_path_part(path: Path) -> bool:
    return any(part.startswith(FORBIDDEN_PREFIXES) for part in path.parts)


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _falsey(value: object) -> bool:
    return value is False or value is None


def _int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _coerce_log_value(value: str) -> object:
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value

"""V1 operator readiness gate for supervised AI Release Radar use."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from radar.daily_review_pack import (
    build_daily_review_pack,
    parse_scheduler_log,
)
from radar.json_utils import write_json


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = ("LAST-", "latest-")
V1_OPERATOR_READY = "V1_OPERATOR_READY"
V1_OPERATOR_READY_WITH_WARNINGS = "V1_OPERATOR_READY_WITH_WARNINGS"
MICRO_FIX_REQUIRED_BEFORE_V1 = "MICRO_FIX_REQUIRED_BEFORE_V1"
BLOCKED = "BLOCKED"
READINESS_GATE_JSON = "1450-V1_Operator_Readiness_Gate.json"
READINESS_GATE_MARKDOWN = "1450-V1_Operator_Readiness_Gate.md"


def evaluate_v1_operator_readiness(
    run_dir: str | Path,
    *,
    daily_review_pack: dict[str, object] | None = None,
    scheduler_log_path: str | Path | None = None,
    dashboard_smoke_status: str = "NOT_RUN",
    action_center_smoke_status: str = "NOT_RUN",
    action_center_run_scope_status: str = "NOT_RUN",
    daily_review_pack_status: str = "PASS",
) -> dict[str, object]:
    """Evaluate the supervised V1 operator readiness classification."""
    root = Path(run_dir).expanduser().resolve()
    pack = daily_review_pack or build_daily_review_pack(root, scheduler_log_path=scheduler_log_path)
    scheduler_evidence = parse_scheduler_log(scheduler_log_path) if scheduler_log_path else {}
    safety = _mapping(pack.get("safety_summary"))
    source_summary = _mapping(pack.get("source_coverage_summary"))
    action_summary = _mapping(pack.get("action_summary"))
    hag_summary = _mapping(pack.get("hag_summary"))

    blockers: list[str] = []
    micro_fixes: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        blockers.append("run_dir_missing")
    if not (root / "0180-Run_Summary.json").is_file():
        blockers.append("run_summary_missing")
    if not (root / "0350-Daily_Sim_Summary.json").is_file():
        blockers.append("daily_sim_summary_missing")
    if scheduler_evidence and scheduler_evidence.get("script_exit_code") not in (0, None):
        blockers.append("scheduler_script_exit_nonzero")
    if dashboard_smoke_status == "FAIL":
        blockers.append("dashboard_smoke_failed")
    if action_center_smoke_status == "FAIL":
        blockers.append("action_center_smoke_failed")
    if not _all_safety_confirmed(safety):
        blockers.append("safety_confirmations_missing")

    if daily_review_pack_status != "PASS":
        micro_fixes.append("daily_review_pack_not_pass")
    if dashboard_smoke_status != "PASS":
        micro_fixes.append("dashboard_smoke_not_pass")
    if action_center_smoke_status != "PASS":
        micro_fixes.append("action_center_smoke_not_pass")
    if action_center_run_scope_status != "PASS":
        micro_fixes.append("action_center_run_scope_not_pass")
    if hag_summary.get("requires_human_approval") is not True:
        micro_fixes.append("hag_hold_not_clear")

    if source_summary.get("coverage_warning") is True:
        warnings.append("source_coverage_low")
    if int(source_summary.get("unsupported_source_count") or 0) > 0:
        warnings.append("unsupported_sources_present")
    if int(source_summary.get("manual_review_required_count") or 0) > 0:
        warnings.append("manual_review_sources_present")
    if int(action_summary.get("direct_actions") or 0) > 0:
        warnings.append("direct_actions_require_human_review")
    if scheduler_evidence.get("no_auto_action_confirmed") is True:
        warnings.append("scheduler_evidence_confirms_no_auto_action")

    if blockers:
        classification = BLOCKED
    elif micro_fixes:
        classification = MICRO_FIX_REQUIRED_BEFORE_V1
    elif warnings:
        classification = V1_OPERATOR_READY_WITH_WARNINGS
    else:
        classification = V1_OPERATOR_READY

    return {
        "schema_version": 1,
        "gate": "1450) V1 Operator Readiness Gate",
        "classification": classification,
        "run_dir": str(root),
        "radar_run_id": pack.get("radar_run_id"),
        "daily_review_pack_status": daily_review_pack_status,
        "dashboard_smoke_status": dashboard_smoke_status,
        "action_center_smoke_status": action_center_smoke_status,
        "action_center_run_scope_status": action_center_run_scope_status,
        "scheduler_evidence": scheduler_evidence,
        "checks": {
            "scheduler_ok": not any(item.startswith("scheduler_") for item in blockers),
            "bridge_ok": root.exists(),
            "dashboard_ok": dashboard_smoke_status == "PASS",
            "action_center_ok": action_center_smoke_status == "PASS",
            "hag_clear": "hag_hold_not_clear" not in micro_fixes,
            "daily_review_pack_ok": daily_review_pack_status == "PASS",
            "safety_ok": "safety_confirmations_missing" not in blockers,
            "source_coverage_warning": source_summary.get("coverage_warning") is True,
        },
        "blockers": blockers,
        "micro_fixes": micro_fixes,
        "warnings": sorted(set(warnings + [str(item) for item in _list(pack.get("warnings"))])),
        "recommended_next_step": _recommended_next_step(classification),
    }


def write_v1_operator_readiness_gate(
    run_dir: str | Path,
    output_dir: str | Path,
    *,
    daily_review_pack: dict[str, object] | None = None,
    scheduler_log_path: str | Path | None = None,
    dashboard_smoke_status: str = "NOT_RUN",
    action_center_smoke_status: str = "NOT_RUN",
    action_center_run_scope_status: str = "NOT_RUN",
    daily_review_pack_status: str = "PASS",
) -> dict[str, str]:
    """Write the V1 readiness gate JSON and Markdown outside the repository."""
    target_dir = _outside_repo_output_dir(output_dir)
    gate = evaluate_v1_operator_readiness(
        run_dir,
        daily_review_pack=daily_review_pack,
        scheduler_log_path=scheduler_log_path,
        dashboard_smoke_status=dashboard_smoke_status,
        action_center_smoke_status=action_center_smoke_status,
        action_center_run_scope_status=action_center_run_scope_status,
        daily_review_pack_status=daily_review_pack_status,
    )
    json_path = target_dir / READINESS_GATE_JSON
    markdown_path = target_dir / READINESS_GATE_MARKDOWN
    write_json(json_path, gate)
    markdown_path.write_text(render_v1_operator_readiness_gate_markdown(gate), encoding="utf-8", newline="\n")
    return {
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "classification": str(gate.get("classification") or "NO_DATA"),
    }


def render_v1_operator_readiness_gate_markdown(gate: dict[str, object]) -> str:
    """Render the V1 readiness gate as Markdown."""
    checks = _mapping(gate.get("checks"))
    lines = [
        "# 1450) V1 Operator Readiness Gate",
        "",
        f"- [F] classification: {gate.get('classification')}.",
        f"- [F] run_dir: {gate.get('run_dir')}.",
        f"- [F] radar_run_id: {gate.get('radar_run_id')}.",
        f"- [F] dashboard_smoke_status: {gate.get('dashboard_smoke_status')}.",
        f"- [F] action_center_smoke_status: {gate.get('action_center_smoke_status')}.",
        f"- [F] action_center_run_scope_status: {gate.get('action_center_run_scope_status')}.",
        "",
        "## Checks",
        "",
    ]
    for key in sorted(checks):
        lines.append(f"- [F] {key}: {str(checks[key]).lower()}.")
    lines.extend(["", "## Blockers", ""])
    blockers = _list(gate.get("blockers"))
    lines.extend(f"- [F] {item}" for item in blockers) if blockers else lines.append("- [F] none")
    lines.extend(["", "## Micro Fixes", ""])
    micro_fixes = _list(gate.get("micro_fixes"))
    lines.extend(f"- [F] {item}" for item in micro_fixes) if micro_fixes else lines.append("- [F] none")
    lines.extend(["", "## Warnings", ""])
    warnings = _list(gate.get("warnings"))
    lines.extend(f"- [F] {item}" for item in warnings) if warnings else lines.append("- [F] none")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- [PROP] {gate.get('recommended_next_step')}.",
        ]
    )
    return "\n".join(lines).rstrip("\n") + "\n"


def _recommended_next_step(classification: str) -> str:
    if classification in {V1_OPERATOR_READY, V1_OPERATOR_READY_WITH_WARNINGS}:
        return (
            "1510) AI Release Radar - V1 Operator RC Review, Publish Flow and "
            "Next Source Coverage Cycle"
        )
    if classification == MICRO_FIX_REQUIRED_BEFORE_V1:
        return "1510) AI Release Radar - V1 Operator RC Micro-Fix Pass Before Publish"
    return "Investigate blocking evidence before V1 operator review."


def _all_safety_confirmed(safety: dict[str, Any]) -> bool:
    required = (
        "no_auto_action",
        "no_email",
        "no_runtime_llm",
        "no_external_notification",
        "no_scheduler_mutation",
    )
    return all(safety.get(key) is True for key in required)


def _outside_repo_output_dir(output_dir: str | Path) -> Path:
    target = Path(output_dir).expanduser().resolve()
    if _is_path_within(target, REPO_ROOT):
        raise ValueError("V1 readiness gate output_dir must be outside repository.")
    if _has_forbidden_path_part(target):
        raise ValueError("V1 readiness gate output_dir must not use LAST-* or latest-* names.")
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


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []

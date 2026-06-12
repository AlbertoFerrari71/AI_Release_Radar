"""Command line interface for AI Release Radar local workflows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import sys
from pathlib import Path

from radar.automation_gate import (
    FAIL,
    evaluate_automation_gate,
    render_automation_gate_markdown,
)
from radar.action_triage import triage_daily_actions
from radar.daily_quality_gate import (
    evaluate_daily_quality_gate,
    render_daily_quality_gate_markdown,
)
from radar.daily_review_pack import write_daily_review_pack
from radar.hag_report import build_hag_report
from radar.json_utils import read_json, write_json
from radar.live_url_check import (
    check_sources_live,
    verification_results_to_dict,
)
from radar.live_snapshot import run_live_snapshot as run_live_snapshot_workflow
from radar.real_run import (
    DEFAULT_REAL_RUN_MAX_BYTES,
    DEFAULT_PROJECT_MAP_PATH,
    REAL_RUN_NEXT_STEP_RECOMMENDATION,
    run_real_radar_report,
)
from radar.report_engine import (
    ReportInput,
    load_report_input,
    render_compact_markdown_report,
    render_full_markdown_report,
    render_report_status,
)
from radar.operator_dashboard import render_operator_dashboard
from radar.project_profiles import load_project_profiles
from radar.prompt_suggestions import (
    render_prompt_suggestion_pack_markdown,
    suggest_codex_prompts,
)
from radar.source_registry import load_source_registry_file
from radar.source_fetcher import (
    fetched_sources_to_dict,
    fetch_sources_content,
)
from radar.supervised_loop import render_supervised_action_loop_dry_run
from radar.v1_readiness import write_v1_operator_readiness_gate


REPO_ROOT = Path(__file__).resolve().parents[1]
DRY_RUN_INPUT_PATH = REPO_ROOT / "examples" / "fixtures" / "0080_report_input.json"
DEFAULT_SOURCE_REGISTRY_PATH = REPO_ROOT / "config" / "sources" / "openai_sources.json"
FULL_REPORT_FILENAME = "0090_dry_run_report_full.md"
COMPACT_REPORT_FILENAME = "0090_dry_run_report_compact.md"
SUMMARY_FILENAME = "0090_dry_run_summary.txt"
CHECK_URLS_RESULTS_FILENAME = "0110_live_url_check_results.json"
CHECK_URLS_SUMMARY_FILENAME = "0110_live_url_check_summary.txt"
FETCH_SOURCES_RESULTS_FILENAME = "0130_fetch_sources_results.json"
FETCH_SOURCES_SUMMARY_FILENAME = "0130_fetch_sources_summary.txt"
NEXT_STEP_RECOMMENDATION = "0100) OpenAI Source Registry and URL Verification"
CHECK_URLS_NEXT_STEP_RECOMMENDATION = (
    "0130) Source Fetcher Skeleton Without Parsing"
)
FETCH_SOURCES_NEXT_STEP_RECOMMENDATION = (
    "0140) Source Fetcher Review and Content Safety Hardening"
)
LIVE_SNAPSHOT_NEXT_STEP_RECOMMENDATION = (
    "0180) First Real Radar Report - Manual Run"
)
REAL_RUN_MANUAL_PROFILE = "manual"
REAL_RUN_MANUAL_TIMEOUT_SECONDS = 30.0
REAL_RUN_MANUAL_MAX_SOURCES = 13
REAL_RUN_MANUAL_MAX_BYTES = 2_000_000
DAILY_SIM_OUTPUT_PREFIX = "0320_0400_daily_sim"
DAILY_SIM_SUMMARY_FILENAME = "0350-Daily_Sim_Summary.json"
DAILY_SIM_GATE_JSON_FILENAME = "0350-Daily_Sim_Gate.json"
DAILY_SIM_GATE_MARKDOWN_FILENAME = "0350-Daily_Sim_Gate.md"
DAILY_QUALITY_GATE_V2_JSON_FILENAME = "0630-Daily_Quality_Gate_V2.json"
DAILY_QUALITY_GATE_V2_MARKDOWN_FILENAME = "0630-Daily_Quality_Gate_V2.md"
ACTION_TRIAGE_JSON_FILENAME = "0650-Action_Triage.json"
PROMPT_SUGGESTIONS_JSON_FILENAME = "0660-Codex_Prompt_Suggestions.json"
PROMPT_SUGGESTIONS_MARKDOWN_FILENAME = "0660-Codex_Prompt_Suggestions.md"
HAG_REPORT_MARKDOWN_FILENAME = "0680-Human_Approval_Gate_Report.md"
DAILY_OPERATOR_DASHBOARD_FILENAME = "0710-Daily_Operator_Dashboard.md"
SUPERVISED_ACTION_LOOP_DRY_RUN_FILENAME = "0730-Supervised_Action_Loop_Dry_Run.md"
DAILY_SIM_NEXT_STEP_RECOMMENDATION = (
    "0750) Alberto reviews HAG decisions and approves the next supervised step."
)


def build_dry_run_report_input() -> ReportInput:
    """Load the deterministic offline fixture used by the dry-run CLI."""
    return load_report_input(read_json(DRY_RUN_INPUT_PATH))


def run_dry_run(output_dir: str, full: bool = True, compact: bool = True) -> dict[str, str]:
    """Run the offline dry-run and write requested outputs to output_dir."""
    if not full and not compact:
        raise ValueError("at least one report output must be enabled.")

    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    report_input = build_dry_run_report_input()
    full_report_path = target_dir / FULL_REPORT_FILENAME
    compact_report_path = target_dir / COMPACT_REPORT_FILENAME
    summary_path = target_dir / SUMMARY_FILENAME

    full_report = str(full_report_path) if full else "skipped"
    compact_report = str(compact_report_path) if compact else "skipped"

    if full:
        _write_text(full_report_path, render_full_markdown_report(report_input))
    if compact:
        _write_text(compact_report_path, render_compact_markdown_report(report_input))

    summary = build_summary(
        status=render_report_status(report_input),
        full_report=full_report,
        compact_report=compact_report,
        summary=str(summary_path),
    )
    _write_text(summary_path, summary)

    return {
        "full_report": full_report,
        "compact_report": compact_report,
        "summary": str(summary_path),
    }


def run_check_urls(
    registry: str,
    output_dir: str,
    timeout_seconds: float = 10.0,
    max_sources: int | None = None,
) -> dict[str, str]:
    """Run the explicit live URL check and write results to output_dir."""
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    sources = load_source_registry_file(registry)
    results = check_sources_live(
        sources,
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
    )
    results_data = verification_results_to_dict(results)

    results_path = target_dir / CHECK_URLS_RESULTS_FILENAME
    summary_path = target_dir / CHECK_URLS_SUMMARY_FILENAME
    write_json(results_path, results_data)
    _write_text(
        summary_path,
        build_check_urls_summary(
            results_data["summary"],
            results_json=str(results_path),
            summary=str(summary_path),
        ),
    )
    return {
        "results_json": str(results_path),
        "summary": str(summary_path),
    }


def run_fetch_sources(
    registry: str,
    output_dir: str,
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int = 4096,
) -> dict[str, str]:
    """Run the explicit live read-only bounded source content fetch."""
    target_dir = Path(output_dir).expanduser().resolve()
    if _is_path_within(target_dir, REPO_ROOT):
        raise ValueError("fetch-sources output_dir must be outside repository.")
    target_dir.mkdir(parents=True, exist_ok=True)

    sources = load_source_registry_file(registry)
    results = fetch_sources_content(
        sources,
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
        max_bytes=max_bytes,
    )
    results_data = fetched_sources_to_dict(results)

    results_path = target_dir / FETCH_SOURCES_RESULTS_FILENAME
    summary_path = target_dir / FETCH_SOURCES_SUMMARY_FILENAME
    write_json(results_path, results_data)
    _write_text(
        summary_path,
        build_fetch_sources_summary(
            results_data["summary"],
            max_bytes=max_bytes,
            results_json=str(results_path),
            summary=str(summary_path),
        ),
    )
    return {
        "results_json": str(results_path),
        "summary": str(summary_path),
    }


def run_live_snapshot(
    source_registry: str,
    output_dir: str,
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int = 65536,
) -> dict[str, object]:
    """Run explicit controlled live snapshot generation."""
    return run_live_snapshot_workflow(
        source_registry=source_registry,
        output_dir=output_dir,
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
        max_bytes=max_bytes,
    ).to_dict()


def run_real_run(
    source_registry: str,
    output_dir: str,
    project_map: str | None = None,
    previous_snapshot_dir: str | None = None,
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int = DEFAULT_REAL_RUN_MAX_BYTES,
) -> dict[str, object]:
    """Run first manual real radar report generation."""
    return run_real_radar_report(
        source_registry=source_registry,
        output_dir=output_dir,
        project_map=project_map,
        previous_snapshot_dir=previous_snapshot_dir,
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
        max_bytes=max_bytes,
    ).to_dict()


def run_daily_sim(
    *,
    output_root: str,
    source_registry: str | None = None,
    project_map: str | None = None,
    previous_snapshot_dir: str | None = None,
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int | None = None,
    stamp: str | None = None,
) -> dict[str, object]:
    """Run a controlled daily simulation without creating any scheduler."""
    root = _outside_repo_output_root(output_root, label="daily-sim output_root")
    effective_stamp = stamp if stamp is not None else _utc_stamp()
    if not effective_stamp.strip():
        raise ValueError("daily-sim stamp must not be empty.")
    target_dir = root / f"{DAILY_SIM_OUTPUT_PREFIX}_{effective_stamp}"
    if target_dir.exists():
        raise ValueError(f"daily-sim output directory already exists: {target_dir}")

    (
        resolved_source_registry,
        resolved_timeout_seconds,
        resolved_max_sources,
        resolved_max_bytes,
    ) = resolve_real_run_config(
        source_registry=source_registry,
        profile=REAL_RUN_MANUAL_PROFILE,
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
        max_bytes=max_bytes,
    )
    result = run_real_run(
        resolved_source_registry,
        str(target_dir),
        project_map=project_map if project_map is not None else str(DEFAULT_PROJECT_MAP_PATH),
        previous_snapshot_dir=previous_snapshot_dir,
        timeout_seconds=resolved_timeout_seconds,
        max_sources=resolved_max_sources,
        max_bytes=resolved_max_bytes,
    )
    gate = evaluate_automation_gate(target_dir)
    gate_json_path = target_dir / DAILY_SIM_GATE_JSON_FILENAME
    gate_markdown_path = target_dir / DAILY_SIM_GATE_MARKDOWN_FILENAME
    write_json(gate_json_path, gate)
    _write_text(gate_markdown_path, render_automation_gate_markdown(gate))
    quality_gate = evaluate_daily_quality_gate(gate)
    quality_gate_json_path = target_dir / DAILY_QUALITY_GATE_V2_JSON_FILENAME
    quality_gate_markdown_path = target_dir / DAILY_QUALITY_GATE_V2_MARKDOWN_FILENAME
    write_json(quality_gate_json_path, quality_gate)
    _write_text(quality_gate_markdown_path, render_daily_quality_gate_markdown(quality_gate))
    project_profiles = load_project_profiles()
    triage = triage_daily_actions(
        {"result": result},
        automation_gate=gate.to_dict(),
        daily_quality_gate=quality_gate.to_dict(),
        project_profiles=project_profiles,
    )
    triage_json_path = target_dir / ACTION_TRIAGE_JSON_FILENAME
    write_json(triage_json_path, triage)
    prompt_suggestions = suggest_codex_prompts(triage)
    prompt_suggestions_json_path = target_dir / PROMPT_SUGGESTIONS_JSON_FILENAME
    prompt_suggestions_markdown_path = target_dir / PROMPT_SUGGESTIONS_MARKDOWN_FILENAME
    write_json(prompt_suggestions_json_path, prompt_suggestions)
    _write_text(
        prompt_suggestions_markdown_path,
        render_prompt_suggestion_pack_markdown(prompt_suggestions),
    )
    hag = build_hag_report(
        {"result": result},
        daily_quality_gate=quality_gate.to_dict(),
        action_triage=triage,
        prompt_suggestions=prompt_suggestions,
    )
    hag_report_path = target_dir / HAG_REPORT_MARKDOWN_FILENAME
    _write_text(hag_report_path, hag.markdown)
    dashboard_path = target_dir / DAILY_OPERATOR_DASHBOARD_FILENAME
    _write_text(
        dashboard_path,
        render_operator_dashboard(
            {"result": result},
            daily_quality_gate=quality_gate.to_dict(),
            action_triage=triage.to_dict(),
            prompt_suggestions=prompt_suggestions.to_dict(),
            hag_status=hag.status,
        ),
    )
    supervised_loop_path = target_dir / SUPERVISED_ACTION_LOOP_DRY_RUN_FILENAME
    _write_text(
        supervised_loop_path,
        render_supervised_action_loop_dry_run(
            action_triage=triage.to_dict(),
            prompt_suggestions=prompt_suggestions.to_dict(),
            hag_status=hag.status,
            dashboard_path=str(dashboard_path),
        ),
    )
    summary_path = target_dir / DAILY_SIM_SUMMARY_FILENAME
    summary_data: dict[str, object] = {
        "schema_version": 1,
        "mode": "daily-sim",
        "status": result.get("status"),
        "automation_gate_status": gate.status,
        "recommendation": gate.recommendation,
        "output_dir": str(target_dir),
        "daily_sim_summary": str(summary_path),
        "automation_gate_json": str(gate_json_path),
        "automation_gate_markdown": str(gate_markdown_path),
        "daily_quality_gate_v2": quality_gate.to_dict(),
        "daily_quality_gate_v2_json": str(quality_gate_json_path),
        "daily_quality_gate_v2_markdown": str(quality_gate_markdown_path),
        "action_triage": triage.to_dict(),
        "action_triage_json": str(triage_json_path),
        "action_triage_status": triage.status,
        "prompt_suggestions": prompt_suggestions.to_dict(),
        "prompt_suggestions_json": str(prompt_suggestions_json_path),
        "prompt_suggestions_markdown": str(prompt_suggestions_markdown_path),
        "prompt_suggestions_count": len(prompt_suggestions.suggestions),
        "hag_status": hag.status,
        "hag_report_markdown": str(hag_report_path),
        "dashboard_path": str(dashboard_path),
        "supervised_action_loop_dry_run": str(supervised_loop_path),
        "manual_review_queue": gate.manual_review_queue,
        "manual_review_queue_count": len(gate.manual_review_queue),
        "scheduler_readiness_recommendation": gate.scheduler_readiness_recommendation,
        "real_run": result,
        "automation_gate": gate.to_dict(),
        "scheduler_activated": False,
        "windows_task_created": False,
        "auto_action_executed": False,
        "other_repository_touched": False,
        "email_sent": False,
        "llm_called": False,
        "next_step": DAILY_SIM_NEXT_STEP_RECOMMENDATION,
    }
    write_json(summary_path, summary_data)
    return summary_data


def run_daily_review_pack(
    *,
    run_dir: str,
    output_dir: str,
    scheduler_log: str | None = None,
) -> dict[str, str]:
    """Generate the Bridge-only Daily Review Pack from an existing run."""
    return write_daily_review_pack(
        run_dir,
        output_dir,
        scheduler_log_path=scheduler_log,
    )


def run_v1_readiness_gate(
    *,
    run_dir: str,
    output_dir: str,
    scheduler_log: str | None = None,
    dashboard_smoke_status: str = "NOT_RUN",
    action_center_smoke_status: str = "NOT_RUN",
    action_center_run_scope_status: str = "NOT_RUN",
    daily_review_pack_status: str = "PASS",
) -> dict[str, str]:
    """Generate the V1 operator readiness gate from existing evidence."""
    return write_v1_operator_readiness_gate(
        run_dir,
        output_dir,
        scheduler_log_path=scheduler_log,
        dashboard_smoke_status=dashboard_smoke_status,
        action_center_smoke_status=action_center_smoke_status,
        action_center_run_scope_status=action_center_run_scope_status,
        daily_review_pack_status=daily_review_pack_status,
    )


def resolve_real_run_config(
    *,
    source_registry: str | None,
    profile: str | None,
    timeout_seconds: float | None,
    max_sources: int | None,
    max_bytes: int | None,
) -> tuple[str, float | None, int | None, int]:
    """Resolve real-run CLI defaults without hiding the output directory."""
    if profile is None:
        if source_registry is None:
            raise ValueError(
                "real-run requires --source-registry unless --profile manual is used."
            )
        return (
            source_registry,
            timeout_seconds,
            max_sources,
            max_bytes if max_bytes is not None else DEFAULT_REAL_RUN_MAX_BYTES,
        )
    if profile != REAL_RUN_MANUAL_PROFILE:
        raise ValueError(f"unsupported real-run profile: {profile}")
    return (
        source_registry if source_registry is not None else str(DEFAULT_SOURCE_REGISTRY_PATH),
        timeout_seconds if timeout_seconds is not None else REAL_RUN_MANUAL_TIMEOUT_SECONDS,
        max_sources if max_sources is not None else REAL_RUN_MANUAL_MAX_SOURCES,
        max_bytes if max_bytes is not None else REAL_RUN_MANUAL_MAX_BYTES,
    )


def build_summary(
    *,
    status: str,
    full_report: str,
    compact_report: str,
    summary: str,
) -> str:
    """Build the deterministic console and file summary."""
    lines = [
        "AI Release Radar dry-run completed",
        f"Status: {status}",
        f"Full report: {full_report}",
        f"Compact report: {compact_report}",
        f"Summary: {summary}",
        f"Next step: {NEXT_STEP_RECOMMENDATION}",
    ]
    return "\n".join(lines) + "\n"


def build_check_urls_summary(
    summary_data: object,
    *,
    results_json: str,
    summary: str,
) -> str:
    """Build the console and file summary for check-urls."""
    if not isinstance(summary_data, dict):
        raise ValueError("summary_data must be a dict.")
    lines = [
        "AI Release Radar live URL check completed",
        f"Total: {summary_data.get('total')}",
        f"OK: {summary_data.get('ok')}",
        f"Failed: {summary_data.get('failed')}",
        f"Redirected: {summary_data.get('redirected')}",
        f"Timeout: {summary_data.get('timeout')}",
        f"Unreachable: {summary_data.get('unreachable')}",
        f"Unexpected status: {summary_data.get('unexpected_status')}",
        f"Disabled: {summary_data.get('disabled')}",
        f"Recommendation: {summary_data.get('recommendation')}",
        f"Results JSON: {results_json}",
        f"Summary: {summary}",
        f"Next step: {CHECK_URLS_NEXT_STEP_RECOMMENDATION}",
    ]
    return "\n".join(lines) + "\n"


def build_fetch_sources_summary(
    summary_data: object,
    *,
    max_bytes: int,
    results_json: str,
    summary: str,
) -> str:
    """Build the console and file summary for fetch-sources."""
    if not isinstance(summary_data, dict):
        raise ValueError("summary_data must be a dict.")
    lines = [
        "AI Release Radar source fetch completed",
        "Mode: live read-only bounded content fetch",
        f"Total: {summary_data.get('total')}",
        f"OK: {summary_data.get('ok')}",
        f"Failed: {summary_data.get('failed')}",
        f"Disabled: {summary_data.get('disabled')}",
        f"Truncated: {summary_data.get('truncated')}",
        f"Unexpected status: {summary_data.get('unexpected_status')}",
        f"Redirect not allowed: {summary_data.get('redirect_not_allowed')}",
        f"Max bytes: {max_bytes}",
        "Parsing: not performed",
        "Snapshot: not created",
        f"Results JSON: {results_json}",
        f"Summary: {summary}",
        f"Next step: {FETCH_SOURCES_NEXT_STEP_RECOMMENDATION}",
    ]
    return "\n".join(lines) + "\n"


def build_live_snapshot_summary(result_data: object) -> str:
    """Build the console summary for controlled live snapshot generation."""
    if not isinstance(result_data, dict):
        raise ValueError("result_data must be a dict.")
    lines = [
        "AI Release Radar live snapshot completed",
        "Mode: explicit live read-only snapshot generation",
        f"Status: {result_data.get('status')}",
        f"Run ID: {result_data.get('run_id')}",
        f"Sources: {result_data.get('source_count')}",
        f"Snapshots: {result_data.get('snapshot_count')}",
        f"Parsed: {result_data.get('parsed_count')}",
        f"Skipped: {result_data.get('skipped_count')}",
        f"Failed: {result_data.get('failed_count')}",
        f"Output dir: {result_data.get('output_dir')}",
        f"Run summary: {result_data.get('run_summary_path')}",
        f"Run index entry: {result_data.get('run_index_entry_path')}",
        f"Runs index: {result_data.get('runs_index_path')}",
        f"Next step: {LIVE_SNAPSHOT_NEXT_STEP_RECOMMENDATION}",
    ]
    return "\n".join(lines) + "\n"


def build_real_run_summary(result_data: object) -> str:
    """Build the console summary for first manual real radar report generation."""
    if not isinstance(result_data, dict):
        raise ValueError("result_data must be a dict.")
    lines = [
        "AI Release Radar real run completed",
        "Mode: explicit live snapshot plus manual report generation",
        f"Status: {result_data.get('status')}",
        f"Run ID: {result_data.get('run_id')}",
        f"Sources: {result_data.get('source_count')}",
        f"Items: {result_data.get('item_count')}",
        f"New: {result_data.get('new_count')}",
        f"Changed: {result_data.get('changed_count')}",
        f"Removed: {result_data.get('removed_count')}",
        f"Project impacts: {result_data.get('project_impact_count')}",
        f"Full report: {result_data.get('report_full')}",
        f"Compact report: {result_data.get('report_compact')}",
        f"Run summary: {result_data.get('run_summary')}",
        f"Runs index: {result_data.get('runs_index')}",
        f"Next step: {REAL_RUN_NEXT_STEP_RECOMMENDATION}",
    ]
    return "\n".join(lines) + "\n"


def build_daily_sim_summary(result_data: object) -> str:
    """Build the console summary for a controlled daily simulation."""
    if not isinstance(result_data, dict):
        raise ValueError("result_data must be a dict.")
    real_run = result_data.get("real_run")
    if not isinstance(real_run, dict):
        raise ValueError("daily-sim result_data must include real_run dict.")
    gate = result_data.get("automation_gate")
    gate_metrics = gate.get("metrics") if isinstance(gate, dict) else {}
    if not isinstance(gate_metrics, dict):
        gate_metrics = {}
    lines = [
        "AI Release Radar daily simulation completed",
        "Mode: controlled daily run simulation",
        f"Status: {result_data.get('status')}",
        f"Run ID: {real_run.get('run_id')}",
        f"Sources: {real_run.get('source_count')}",
        f"Parsed: {real_run.get('parsed_count')}",
        f"Items: {real_run.get('item_count')}",
        f"Direct actions: {real_run.get('direct_action_count')}",
        f"Monitor-only actions: {real_run.get('monitor_only_action_count')}",
        f"Manual review required: {gate_metrics.get('manual_review_required_count')}",
        f"Unsupported sources: {real_run.get('unsupported_source_count')}",
        f"Manual review queue: {result_data.get('manual_review_queue_count')}",
        f"Report scorecard: {gate_metrics.get('report_scorecard_status')}",
        f"Automation gate: {result_data.get('automation_gate_status')}",
        (
            "Daily quality gate: "
            f"{_daily_quality_status(result_data)}"
        ),
        f"Action triage: {result_data.get('action_triage_status')}",
        f"Prompt suggestions: {result_data.get('prompt_suggestions_count')}",
        f"HAG status: {result_data.get('hag_status')}",
        f"Dashboard: {result_data.get('dashboard_path')}",
        f"Recommendation: {result_data.get('recommendation')}",
        (
            "Scheduler readiness: "
            f"{result_data.get('scheduler_readiness_recommendation')}"
        ),
        f"Output dir: {result_data.get('output_dir')}",
        f"Run summary: {real_run.get('run_summary')}",
        f"Gate report: {result_data.get('automation_gate_markdown')}",
        f"Daily sim summary: {result_data.get('daily_sim_summary')}",
        "No scheduler: confirmed",
        "No Windows task: confirmed",
        "No auto-action: confirmed",
        "No other repo touched: confirmed",
        "No email: confirmed",
        "No LLM: confirmed",
        f"Next step: {result_data.get('next_step')}",
    ]
    return "\n".join(lines) + "\n"


def build_daily_review_pack_summary(result_data: object) -> str:
    """Build console summary for Daily Review Pack generation."""
    if not isinstance(result_data, dict):
        raise ValueError("daily review pack result_data must be a dict.")
    lines = [
        "AI Release Radar daily review pack completed",
        f"Status: {result_data.get('status')}",
        f"Run ID: {result_data.get('run_id')}",
        f"Markdown: {result_data.get('markdown_path')}",
        f"JSON: {result_data.get('json_path')}",
        "No auto-action: confirmed",
        "No email: confirmed",
        "No LLM: confirmed",
    ]
    return "\n".join(lines) + "\n"


def build_v1_readiness_gate_summary(result_data: object) -> str:
    """Build console summary for V1 readiness gate generation."""
    if not isinstance(result_data, dict):
        raise ValueError("V1 readiness gate result_data must be a dict.")
    lines = [
        "AI Release Radar V1 readiness gate completed",
        f"Classification: {result_data.get('classification')}",
        f"Markdown: {result_data.get('markdown_path')}",
        f"JSON: {result_data.get('json_path')}",
        "No auto-action: confirmed",
        "No email: confirmed",
        "No LLM: confirmed",
    ]
    return "\n".join(lines) + "\n"


def _daily_quality_status(result_data: dict[str, object]) -> object:
    quality_gate = result_data.get("daily_quality_gate_v2")
    if isinstance(quality_gate, dict):
        return quality_gate.get("overall_daily_review_status")
    return None


def build_arg_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m radar.cli",
        description="AI Release Radar offline CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dry_run = subparsers.add_parser(
        "dry-run",
        help="Run the deterministic offline dry-run from local fixtures.",
    )
    dry_run.add_argument(
        "--output-dir",
        required=True,
        help="Explicit directory where dry-run outputs are written.",
    )
    dry_run.add_argument(
        "--compact-only",
        action="store_true",
        help="Write only compact report and summary.",
    )
    dry_run.add_argument(
        "--full-only",
        action="store_true",
        help="Write only full report and summary.",
    )
    check_urls = subparsers.add_parser(
        "check-urls",
        help="Run the explicit live read-only URL check from a source registry.",
    )
    check_urls.add_argument(
        "--registry",
        required=True,
        help=f"Source registry JSON path. Default project registry: {DEFAULT_SOURCE_REGISTRY_PATH}",
    )
    check_urls.add_argument(
        "--output-dir",
        required=True,
        help="Explicit directory where URL check outputs are written.",
    )
    check_urls.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Optional maximum number of registry sources to check.",
    )
    check_urls.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="Per-source timeout in seconds.",
    )
    fetch_sources = subparsers.add_parser(
        "fetch-sources",
        help="Run the explicit live read-only bounded source content fetch.",
    )
    fetch_sources.add_argument(
        "--registry",
        required=True,
        help=f"Source registry JSON path. Default project registry: {DEFAULT_SOURCE_REGISTRY_PATH}",
    )
    fetch_sources.add_argument(
        "--output-dir",
        required=True,
        help="Explicit directory where bounded source content outputs are written.",
    )
    fetch_sources.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Optional maximum number of registry sources to fetch.",
    )
    fetch_sources.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Optional per-source timeout in seconds. Registry value or safe default is used when omitted.",
    )
    fetch_sources.add_argument(
        "--max-bytes",
        type=int,
        default=4096,
        help="Global maximum response body bytes per source; registry max_bytes overrides when set.",
    )
    live_snapshot = subparsers.add_parser(
        "live-snapshot",
        help="Run explicit live read-only snapshot generation from a source registry.",
    )
    live_snapshot.add_argument(
        "--source-registry",
        required=True,
        help=f"Source registry JSON path. Default project registry: {DEFAULT_SOURCE_REGISTRY_PATH}",
    )
    live_snapshot.add_argument(
        "--output-dir",
        required=True,
        help="Explicit outside-repository directory where live snapshot outputs are written.",
    )
    live_snapshot.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Optional maximum number of enabled registry sources to snapshot.",
    )
    live_snapshot.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Optional per-source timeout in seconds. Registry value or safe default is used when omitted.",
    )
    live_snapshot.add_argument(
        "--max-bytes",
        type=int,
        default=65536,
        help="Global maximum response body bytes per source; registry max_bytes overrides when set.",
    )
    real_run = subparsers.add_parser(
        "real-run",
        help="Run explicit live snapshot plus first manual radar report generation.",
    )
    real_run.add_argument(
        "--profile",
        choices=[REAL_RUN_MANUAL_PROFILE],
        default=None,
        help=(
            "Optional safe manual profile. Keeps --output-dir explicit and uses "
            "the default source registry, max 13 sources, 30 second timeout and "
            "2,000,000 max bytes when those options are omitted."
        ),
    )
    real_run.add_argument(
        "--source-registry",
        default=None,
        help=(
            "Source registry JSON path. Required unless --profile manual is used. "
            f"Default project registry: {DEFAULT_SOURCE_REGISTRY_PATH}"
        ),
    )
    real_run.add_argument(
        "--output-dir",
        required=True,
        help="Explicit outside-repository directory where real run outputs are written.",
    )
    real_run.add_argument(
        "--project-map",
        default=str(DEFAULT_PROJECT_MAP_PATH),
        help="Project map JSON path used for impact mapping.",
    )
    real_run.add_argument(
        "--previous-snapshot-dir",
        default=None,
        help="Optional directory with previous 0170-Snapshot_*.json files.",
    )
    real_run.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Optional maximum number of enabled registry sources to fetch.",
    )
    real_run.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Optional per-source timeout in seconds. Registry value or safe default is used when omitted.",
    )
    real_run.add_argument(
        "--max-bytes",
        type=int,
        default=None,
        help="Global maximum response body bytes per source; registry max_bytes overrides when set.",
    )
    daily_sim = subparsers.add_parser(
        "daily-sim",
        help="Run a controlled daily simulation without creating a scheduler.",
    )
    daily_sim.add_argument(
        "--output-root",
        required=True,
        help="Explicit outside-repository root where the dated daily simulation directory is created.",
    )
    daily_sim.add_argument(
        "--source-registry",
        default=None,
        help=(
            "Optional source registry JSON path. Defaults to the manual real-run registry."
        ),
    )
    daily_sim.add_argument(
        "--project-map",
        default=str(DEFAULT_PROJECT_MAP_PATH),
        help="Project map JSON path used for impact mapping.",
    )
    daily_sim.add_argument(
        "--previous-snapshot-dir",
        default=None,
        help="Optional directory with previous 0170-Snapshot_*.json files.",
    )
    daily_sim.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Optional maximum number of enabled registry sources to fetch.",
    )
    daily_sim.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Optional per-source timeout in seconds. Manual profile default is used when omitted.",
    )
    daily_sim.add_argument(
        "--max-bytes",
        type=int,
        default=None,
        help="Global maximum response body bytes per source; manual profile default is used when omitted.",
    )
    review_pack = subparsers.add_parser(
        "daily-review-pack",
        help="Generate a Bridge-only Daily Review Pack from an existing run.",
    )
    review_pack.add_argument(
        "--run-dir",
        required=True,
        help="Existing daily-sim run directory to read.",
    )
    review_pack.add_argument(
        "--output-dir",
        required=True,
        help="Explicit outside-repository directory where the pack is written.",
    )
    review_pack.add_argument(
        "--scheduler-log",
        default=None,
        help="Optional existing scheduler log to summarize as evidence.",
    )
    v1_gate = subparsers.add_parser(
        "v1-readiness-gate",
        help="Generate the V1 operator readiness gate from existing evidence.",
    )
    v1_gate.add_argument(
        "--run-dir",
        required=True,
        help="Existing daily-sim run directory to read.",
    )
    v1_gate.add_argument(
        "--output-dir",
        required=True,
        help="Explicit outside-repository directory where the gate is written.",
    )
    v1_gate.add_argument(
        "--scheduler-log",
        default=None,
        help="Optional existing scheduler log to summarize as evidence.",
    )
    v1_gate.add_argument(
        "--dashboard-smoke-status",
        choices=["PASS", "FAIL", "NOT_RUN"],
        default="NOT_RUN",
        help="Dashboard smoke result from existing evidence.",
    )
    v1_gate.add_argument(
        "--action-center-smoke-status",
        choices=["PASS", "FAIL", "NOT_RUN"],
        default="NOT_RUN",
        help="Action Center smoke result from existing evidence.",
    )
    v1_gate.add_argument(
        "--action-center-run-scope-status",
        choices=["PASS", "FAIL", "NOT_RUN"],
        default="NOT_RUN",
        help="Action Center current-run scope check result.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint returning a process-style exit code."""
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "dry-run":
            if args.compact_only and args.full_only:
                parser.error("--compact-only and --full-only cannot be used together.")
            result = run_dry_run(
                args.output_dir,
                full=not args.compact_only,
                compact=not args.full_only,
            )
            summary = Path(result["summary"]).read_text(encoding="utf-8")
            sys.stdout.write(summary)
            return 0
        if args.command == "check-urls":
            result = run_check_urls(
                args.registry,
                args.output_dir,
                timeout_seconds=args.timeout_seconds,
                max_sources=args.max_sources,
            )
            summary = Path(result["summary"]).read_text(encoding="utf-8")
            sys.stdout.write(summary)
            return 0
        if args.command == "fetch-sources":
            result = run_fetch_sources(
                args.registry,
                args.output_dir,
                timeout_seconds=args.timeout_seconds,
                max_sources=args.max_sources,
                max_bytes=args.max_bytes,
            )
            summary = Path(result["summary"]).read_text(encoding="utf-8")
            sys.stdout.write(summary)
            return 0
        if args.command == "live-snapshot":
            result = run_live_snapshot(
                args.source_registry,
                args.output_dir,
                timeout_seconds=args.timeout_seconds,
                max_sources=args.max_sources,
                max_bytes=args.max_bytes,
            )
            sys.stdout.write(build_live_snapshot_summary(result))
            return 0
        if args.command == "real-run":
            try:
                (
                    source_registry,
                    timeout_seconds,
                    max_sources,
                    max_bytes,
                ) = resolve_real_run_config(
                    source_registry=args.source_registry,
                    profile=args.profile,
                    timeout_seconds=args.timeout_seconds,
                    max_sources=args.max_sources,
                    max_bytes=args.max_bytes,
                )
            except ValueError as exc:
                parser.error(str(exc))
            result = run_real_run(
                source_registry,
                args.output_dir,
                project_map=args.project_map,
                previous_snapshot_dir=args.previous_snapshot_dir,
                timeout_seconds=timeout_seconds,
                max_sources=max_sources,
                max_bytes=max_bytes,
            )
            sys.stdout.write(build_real_run_summary(result))
            return 0
        if args.command == "daily-sim":
            result = run_daily_sim(
                output_root=args.output_root,
                source_registry=args.source_registry,
                project_map=args.project_map,
                previous_snapshot_dir=args.previous_snapshot_dir,
                timeout_seconds=args.timeout_seconds,
                max_sources=args.max_sources,
                max_bytes=args.max_bytes,
            )
            sys.stdout.write(build_daily_sim_summary(result))
            return 1 if result.get("automation_gate_status") == FAIL else 0
        if args.command == "daily-review-pack":
            result = run_daily_review_pack(
                run_dir=args.run_dir,
                output_dir=args.output_dir,
                scheduler_log=args.scheduler_log,
            )
            sys.stdout.write(build_daily_review_pack_summary(result))
            return 0
        if args.command == "v1-readiness-gate":
            result = run_v1_readiness_gate(
                run_dir=args.run_dir,
                output_dir=args.output_dir,
                scheduler_log=args.scheduler_log,
                dashboard_smoke_status=args.dashboard_smoke_status,
                action_center_smoke_status=args.action_center_smoke_status,
                action_center_run_scope_status=args.action_center_run_scope_status,
            )
            sys.stdout.write(build_v1_readiness_gate_summary(result))
            return 0 if result.get("classification") != "BLOCKED" else 1
        parser.error(f"unsupported command: {args.command}")
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    except Exception as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    return 1


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _outside_repo_output_root(output_root: str, *, label: str) -> Path:
    target = Path(output_root).expanduser().resolve()
    if _is_path_within(target, REPO_ROOT):
        raise ValueError(f"{label} must be outside repository.")
    if _has_forbidden_path_part(target):
        raise ValueError(f"{label} must not use LAST-* or latest-* names.")
    target.mkdir(parents=True, exist_ok=True)
    return target


def _has_forbidden_path_part(path: Path) -> bool:
    return any(part.startswith("LAST-") or part.startswith("latest-") for part in path.parts)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


if __name__ == "__main__":
    raise SystemExit(main())

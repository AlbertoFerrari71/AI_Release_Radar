"""FastAPI app for the local AI Release Radar web dashboard."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from radar.news_translation import apply_translation_cache_to_actions
from radar_web.action_center import (
    build_action_center_payload,
    export_current_backlog,
    generate_prompt_for_action,
    get_action,
    record_decision,
)
from radar_web.config import DashboardConfig, default_config
from radar_web.i18n import (
    SUPPORTED_LOCALES,
    format_bool_for_locale,
    format_catalog_value_for_locale,
    format_datetime_for_locale,
    format_status_for_locale,
    normalize_locale,
    translate,
)
from radar_web.manual_trigger import DailySimTrigger
from radar_web.models import ApiMessage, DashboardStatus
from radar_web.run_locator import inspect_runs_root, list_recent_runs, load_run_detail
from radar_web.scheduler_status import read_scheduler_status


def create_app(
    config: DashboardConfig | None = None,
    *,
    daily_sim_trigger: DailySimTrigger | None = None,
) -> FastAPI:
    """Create the local dashboard app."""
    dashboard_config = config or default_config()
    package_root = Path(__file__).resolve().parent
    templates = Jinja2Templates(directory=str(package_root / "templates"))
    templates.env.filters["status_class"] = status_class
    templates.env.filters["human_datetime"] = human_datetime
    templates.env.filters["yes_no"] = yes_no
    app = FastAPI(
        title="AI Release Radar Local Dashboard",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
    )
    app.state.dashboard_config = dashboard_config
    app.state.daily_sim_trigger = daily_sim_trigger or DailySimTrigger(dashboard_config)
    app.mount(
        "/static",
        StaticFiles(directory=str(package_root / "static")),
        name="static",
    )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> Any:
        runs = list_recent_runs(dashboard_config.runs_root, limit=20)
        status = build_status(dashboard_config, runs=runs).to_dict()
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "status": status,
                "latest": status.get("latest_run"),
                "runs": [run.to_dict() for run in runs],
                **_localized_context(request),
            },
        )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "mode": "local_dashboard",
            "host": dashboard_config.host,
            "port": dashboard_config.port,
            "read_only_default": True,
        }

    @app.get("/api/status")
    def api_status(lang: str | None = None) -> dict[str, Any]:
        data = build_status(dashboard_config).to_dict()
        locale = normalize_locale(lang)
        if lang is not None:
            data["locale"] = locale
            data["status_label"] = format_status_for_locale(data.get("status"), locale)
        return data

    @app.get("/api/runs")
    def api_runs(limit: int = 20, lang: str | None = None) -> dict[str, Any]:
        bounded_limit = max(1, min(limit, 100))
        runs = list_recent_runs(dashboard_config.runs_root, limit=bounded_limit)
        return {
            "runs_root": str(dashboard_config.runs_root),
            "limit": bounded_limit,
            "locale": normalize_locale(lang) if lang is not None else None,
            "runs": [run.to_dict() for run in runs],
        }

    @app.get("/actions", response_class=HTMLResponse)
    def actions(request: Request, filter: str = "all") -> Any:
        localized_context = _localized_context(request)
        payload = build_action_center_payload(dashboard_config, filter_value=filter)
        localized_actions = apply_translation_cache_to_actions(
            payload["actions"],
            run_id=payload.get("run_id"),
            locale=localized_context["lang"],
            bridge_root=dashboard_config.bridge_root,
        )
        localized_actions = _localize_action_center_fields(
            localized_actions,
            localized_context["lang"],
        )
        return templates.TemplateResponse(
            request,
            "actions.html",
            {
                "payload": payload,
                "actions": localized_actions,
                "filters": payload["filters"],
                "selected_filter": payload["selected_filter"],
                **localized_context,
            },
        )

    @app.get("/api/actions")
    def api_actions(filter: str = "all", limit: int = 10, lang: str | None = None) -> dict[str, Any]:
        payload = build_action_center_payload(
            dashboard_config,
            filter_value=filter,
            limit=limit,
        )
        if lang is not None:
            locale = normalize_locale(lang)
            payload["locale"] = locale
            payload["actions"] = apply_translation_cache_to_actions(
                payload["actions"],
                run_id=payload.get("run_id"),
                locale=locale,
                bridge_root=dashboard_config.bridge_root,
            )
            payload["actions"] = _localize_action_center_fields(payload["actions"], locale)
            payload["all_actions"] = apply_translation_cache_to_actions(
                payload["all_actions"],
                run_id=payload.get("run_id"),
                locale=locale,
                bridge_root=dashboard_config.bridge_root,
            )
            payload["all_actions"] = _localize_action_center_fields(
                payload["all_actions"],
                locale,
            )
        return payload

    @app.post("/api/actions/export-backlog")
    def api_actions_export_backlog() -> JSONResponse:
        result = export_current_backlog(dashboard_config)
        status_code = 200 if result["status"] in {"PASS", "NO_DATA"} else 400
        return JSONResponse(result, status_code=status_code)

    @app.get("/api/actions/{action_id}")
    def api_action_detail(action_id: str) -> dict[str, Any]:
        action = get_action(dashboard_config, action_id)
        if action is None:
            raise HTTPException(
                status_code=404,
                detail=ApiMessage(
                    status="NO_DATA",
                    message=f"Action not found: {action_id}",
                ).to_dict(),
            )
        return action.to_dict()

    @app.post("/api/actions/{action_id}/decision")
    async def api_action_decision(action_id: str, request: Request) -> JSONResponse:
        payload = await _json_payload(request)
        result = record_decision(
            dashboard_config,
            action_id,
            decision=str(payload.get("decision") or ""),
            reason=str(payload.get("reason") or ""),
            operator=str(payload.get("operator") or "Alberto"),
        )
        status_code = 200 if result["status"] == "PASS" else 400
        return JSONResponse(result, status_code=status_code)

    @app.post("/api/actions/{action_id}/generate-prompt")
    def api_action_generate_prompt(action_id: str) -> JSONResponse:
        result = generate_prompt_for_action(dashboard_config, action_id)
        status_code = 200 if result["status"] == "PASS" else 400
        return JSONResponse(result, status_code=status_code)

    @app.get("/api/runs/{run_id}")
    def api_run_detail(run_id: str) -> dict[str, Any]:
        return _run_detail_or_404(dashboard_config, run_id)

    @app.get("/api/runs/{run_id}/compact")
    def api_run_compact(run_id: str) -> dict[str, Any]:
        detail = _run_detail_or_404(dashboard_config, run_id)
        return detail["compact_report"]

    @app.get("/api/runs/{run_id}/gate")
    def api_run_gate(run_id: str) -> dict[str, Any]:
        detail = _run_detail_or_404(dashboard_config, run_id)
        return detail["gate_report"]

    @app.get("/api/runs/{run_id}/hag")
    def api_run_hag(run_id: str) -> dict[str, Any]:
        detail = _run_detail_or_404(dashboard_config, run_id)
        return {
            "hag_report": detail["hag_report"],
            "blocked_actions": detail["blocked_actions"],
            "prompt_suggestions": detail["prompt_suggestions"],
            "prompt_suggestions_status": detail["prompt_suggestions_status"],
            "no_auto_action": detail["no_auto_action"],
            "warnings": detail["warnings"],
        }

    @app.get("/api/runs/{run_id}/dashboard")
    def api_run_dashboard(run_id: str) -> dict[str, Any]:
        detail = _run_detail_or_404(dashboard_config, run_id)
        return {
            "operator_dashboard": detail["operator_dashboard"],
            "source_diagnostics_summary": detail["source_diagnostics_summary"],
            "direct_actions": detail["direct_actions"],
            "monitor_only_summary": detail["monitor_only_summary"],
            "manual_review_queue": detail["manual_review_queue"],
            "warnings": detail["warnings"],
        }

    @app.get("/api/runs/{run_id}/source-matrix")
    def api_run_source_matrix(run_id: str) -> dict[str, Any]:
        detail = _run_detail_or_404(dashboard_config, run_id)
        return {
            "run_id": run_id,
            "source_coverage_summary": detail["source_coverage_summary"],
            "source_coverage_matrix": detail["source_coverage_matrix"],
            "no_auto_action": True,
            "warnings": detail["warnings"],
        }

    @app.get("/api/scheduler")
    def api_scheduler() -> dict[str, Any]:
        return read_scheduler_status_placeholder(dashboard_config)

    @app.post("/api/daily-sim/run")
    def api_daily_sim_run() -> JSONResponse:
        result = app.state.daily_sim_trigger.run_now()
        data = result.to_dict()
        if result.status == "ALREADY_RUNNING":
            return JSONResponse(data, status_code=409)
        if result.status == "REFUSED":
            return JSONResponse(data, status_code=400)
        return JSONResponse(data)

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    def run_detail(request: Request, run_id: str) -> Any:
        detail = _run_detail_or_404(dashboard_config, run_id)
        return templates.TemplateResponse(
            request,
            "run_detail.html",
            {
                "detail": detail,
                "run": detail["run"],
                **_localized_context(request),
            },
        )

    return app


def build_status(
    config: DashboardConfig,
    *,
    runs: list[Any] | None = None,
) -> DashboardStatus:
    """Build a top-level read-only dashboard status."""
    recent_runs = runs if runs is not None else list_recent_runs(config.runs_root, limit=20)
    latest = recent_runs[0].to_dict() if recent_runs else None
    warnings = list(config.validate_output_root())
    if not config.bridge_root.exists():
        warnings.append("bridge_root_missing")
    if not config.runs_root.exists():
        warnings.append("runs_root_missing")
    warnings.extend(inspect_runs_root(config.runs_root))
    data_warnings = list(warnings)
    if isinstance(latest, dict):
        data_warnings.extend(str(warning) for warning in latest.get("warnings", []))
    data_warnings = sorted(set(data_warnings))
    return DashboardStatus(
        status=latest.get("status", "NO_DATA") if isinstance(latest, dict) else "NO_DATA",
        bridge_runs_root=str(config.runs_root),
        latest_run=latest,
        recent_run_count=len(recent_runs),
        scheduler=read_scheduler_status_placeholder(config),
        data_completeness_status=_data_completeness_status(
            has_runs=bool(recent_runs),
            warnings=data_warnings,
        ),
        data_completeness_warnings=tuple(data_warnings),
        manual_trigger_enabled=True,
        warnings=tuple(sorted(set(warnings))),
    )


def read_scheduler_status_placeholder(config: DashboardConfig) -> dict[str, Any]:
    """Return read-only scheduler status for the configured task."""
    return read_scheduler_status(config.scheduler_task_name)


def _localized_context(request: Request) -> dict[str, Any]:
    locale = normalize_locale(request.query_params.get("lang"))

    def t(key: str, **kwargs: object) -> str:
        return translate(key, locale, **kwargs)

    def url_with_lang(path: str, **params: object) -> str:
        query = {key: value for key, value in params.items() if value is not None}
        query["lang"] = locale
        return f"{path}?{urlencode(query)}"

    def url_for_locale(target_locale: str) -> str:
        query = dict(request.query_params)
        query["lang"] = normalize_locale(target_locale)
        return f"{request.url.path}?{urlencode(query)}"

    def format_datetime(value: object) -> str:
        return format_datetime_for_locale(value, locale)

    def format_status(value: object) -> str:
        return format_status_for_locale(value, locale)

    def format_bool(value: object) -> str:
        return format_bool_for_locale(value, locale)

    def format_code(value: object) -> str:
        return format_catalog_value_for_locale("code_label", value, locale)

    def format_run_file_key(value: object) -> str:
        return format_catalog_value_for_locale("run_file", value, locale)

    def format_action_title(value: object) -> str:
        return _localize_action_title(str(value or ""), locale)

    def format_project_name(value: object) -> str:
        return _localize_project_name(str(value or ""), locale)

    def format_action_reasons(values: object) -> list[str]:
        raw_values = values if isinstance(values, (list, tuple)) else [values]
        return [
            _localize_reason(str(value), locale)
            for value in raw_values
            if str(value or "").strip()
        ]

    def format_action_next_step(action: object) -> str:
        return _localize_action_next_step(action if isinstance(action, dict) else {}, locale)

    return {
        "lang": locale,
        "supported_locales": SUPPORTED_LOCALES,
        "t": t,
        "url_with_lang": url_with_lang,
        "url_for_locale": url_for_locale,
        "format_datetime": format_datetime,
        "format_status": format_status,
        "format_bool": format_bool,
        "format_code": format_code,
        "format_run_file_key": format_run_file_key,
        "format_action_title": format_action_title,
        "format_project_name": format_project_name,
        "format_action_reasons": format_action_reasons,
        "format_action_next_step": format_action_next_step,
    }


def _localize_action_center_fields(
    actions: list[dict[str, Any]],
    locale: str,
) -> list[dict[str, Any]]:
    """Attach deterministic localized display fields for generated action metadata."""
    return [_localize_action_dict(action, locale) for action in actions]


def _localize_action_dict(action: dict[str, Any], locale: str) -> dict[str, Any]:
    item = dict(action)
    title = str(item.get("localized_title") or item.get("title") or "")
    summary = str(item.get("localized_summary") or item.get("summary") or "")
    if locale != "en":
        item["localized_title"] = _localize_action_title(title, locale)
        item["localized_summary"] = _localize_action_summary(summary, locale)
    item["localized_routing_reasons"] = [
        _localize_reason(str(reason), locale)
        for reason in item.get("routing_reasons", [])
        if str(reason or "").strip()
    ]
    item["localized_noise_reasons"] = [
        _localize_reason(str(reason), locale)
        for reason in item.get("noise_reasons", [])
        if str(reason or "").strip()
    ]
    item["localized_recommended_next_step"] = _localize_action_next_step(item, locale)
    return item


def _localize_action_title(value: str, locale: str) -> str:
    text = value.strip()
    if not text:
        return translate("status_label.no_data", locale)
    if locale == "en":
        return text
    if text.startswith("Review ambiguous radar signal: "):
        subject = _localize_action_title(
            text.removeprefix("Review ambiguous radar signal: "),
            locale,
        )
        return translate("action_title.ambiguous_radar_signal", locale, subject=subject)
    if text.startswith("Manual review: "):
        return translate(
            "action_title.manual_review_source",
            locale,
            source=text.removeprefix("Manual review: "),
        )
    mapping = {
        "Aggregate direct actions": "action_title.aggregate_direct_actions",
        "Aggregate monitor-only actions": "action_title.aggregate_monitor_only_actions",
        "Prompt suggestion": "action_title.instruction_suggestion",
        "Radar action": "action_title.radar_action",
    }
    key = mapping.get(text)
    return translate(key, locale) if key else text


def _localize_action_summary(value: str, locale: str) -> str:
    text = value.strip()
    if not text:
        return translate("status_label.no_data", locale)
    if locale == "en":
        return text
    parts = [part.strip() for part in text.split(";") if part.strip()]
    localized = [_localize_reason(part, locale) for part in parts]
    return "; ".join(localized) if localized else text


def _localize_reason(value: str, locale: str) -> str:
    text = value.strip()
    if not text:
        return translate("status_label.no_data", locale)
    if locale == "en":
        return text
    sentence_mapping = {
        "direct actions exist, but source coverage is below full-pass threshold": (
            "reason_label.direct_actions_below_threshold"
        ),
        "monitor-only actions stay visible but do not become work automatically": (
            "reason_label.monitor_only_stays_visible"
        ),
        "recurring low-score monitor-only action remains monitor": (
            "reason_label.recurring_low_score_monitor"
        ),
        "previously ignored actions cannot stay high priority": (
            "reason_label.previously_ignored_low_priority"
        ),
        "already backlogged actions are shown without escalation": (
            "reason_label.already_listed_no_escalation"
        ),
    }
    if text in sentence_mapping:
        return translate(sentence_mapping[text], locale)
    if "=" in text:
        key, raw_value = text.split("=", 1)
        label = format_catalog_value_for_locale("code_label", key, locale)
        value_label = _localize_project_name(raw_value, locale)
        return f"{label}: {value_label}"
    return format_status_for_locale(text, locale)


def _localize_project_name(value: str, locale: str) -> str:
    text = value.strip()
    if locale == "en":
        return text
    mapping = {
        "Radar source coverage": "project_label.radar_source_coverage",
        "Ambiguous project": "project_label.ambiguous_project",
        "Mixed project targets": "project_label.mixed_project_targets",
    }
    key = mapping.get(text)
    return translate(key, locale) if key else text


def _localize_action_next_step(action: dict[str, Any], locale: str) -> str:
    raw_project = str(action.get("project_name") or action.get("target_project") or "")
    project_name = _localize_project_name(raw_project, locale) if raw_project else ""
    if locale == "en":
        return str(action.get("recommended_next_step") or "")
    decision_status = str(action.get("decision_status") or "")
    action_type = str(action.get("action_type") or "")
    if decision_status == "backlog":
        return translate("action_next.keep_backlog", locale, project=project_name)
    if decision_status == "ignored":
        return translate("action_next.keep_ignored", locale, project=project_name)
    if action_type == "monitor_only":
        return translate("action_next.monitor_only", locale, project=project_name)
    if action_type == "prepare_prompt":
        return translate("action_next.prepare_instructions", locale, project=project_name)
    return translate("action_next.review_impact", locale, project=project_name)


def _data_completeness_status(*, has_runs: bool, warnings: list[str]) -> str:
    if not has_runs:
        return "NO_DATA"
    return "PASS_WITH_WARNINGS" if warnings else "PASS"


def _run_detail_or_404(config: DashboardConfig, run_id: str) -> dict[str, Any]:
    detail = load_run_detail(config.runs_root, run_id)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail=ApiMessage(
                status="NO_DATA",
                message=f"Run not found: {run_id}",
            ).to_dict(),
        )
    return detail


def status_class(value: object) -> str:
    """Map status values to CSS status classes."""
    status = str(value or "NO_DATA").upper()
    if status in {
        "PASS",
        "READY",
        "OK",
        "YES",
        "NO_ACTION_REQUIRED",
        "SAFE_PROMPT_ONLY",
        "LOW",
        "CACHED",
        "SOURCE",
        "TRANSLATED",
        "V1_OPERATOR_READY",
        "RUN_SCOPED",
    }:
        return "status-pass"
    if status in {
        "RUNNING",
        "SUGGESTED_ONLY",
        "MEDIUM",
        "VISIBLE",
        "RECURRING",
        "NEEDS_REVIEW",
        "CHANGES_FOUND",
        "ACTION_RECOMMENDED",
        "RUN_OUTPUT_ONLY",
    }:
        return "status-review"
    if status in {
        "PASS_WITH_WARNINGS",
        "WARN",
        "WARNING",
        "MONITOR",
        "DOWNGRADED",
        "V1_OPERATOR_READY_WITH_WARNINGS",
    }:
        return "status-warn"
    if status == "ACTION_REVIEW_REQUIRED":
        return "status-review"
    if status in {
        "HOLD",
        "HOLD_FOR_HUMAN_APPROVAL",
        "HUMAN_APPROVAL_REQUIRED",
        "REQUIRES_HUMAN_APPROVAL",
        "HIGH",
        "SUPPRESSED",
        "ALREADY_BACKLOGGED",
        "PREVIOUSLY_IGNORED",
        "PROMPT_ALREADY_GENERATED",
        "MICRO_FIX_REQUIRED_BEFORE_V1",
    }:
        return "status-hold"
    if status in {"FAIL", "FAIL_STOP", "BLOCKED_AUTO_ACTION", "FAILED"}:
        return "status-fail"
    if status == "MISSING":
        return "status-no-data"
    return "status-no-data"


def human_datetime(value: object) -> str:
    """Format ISO-like datetimes for the operator UI."""
    if value is None:
        return "NO_DATA"
    text = str(value).strip()
    if not text or text == "NO_DATA":
        return "NO_DATA"
    normalized = text.replace("Z", "+00:00")
    normalized = re.sub(r"(\.\d{6})\d+([+-]\d{2}:\d{2})$", r"\1\2", normalized)
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return text
    return parsed.strftime("%d/%m/%Y %H:%M")


def yes_no(value: object) -> str:
    """Render booleans as operator-readable text."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value) if value is not None else "NO_DATA"


async def _json_payload(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the local web dashboard CLI parser."""
    parser = argparse.ArgumentParser(
        prog="python -m radar_web.app",
        description="Run the local AI Release Radar dashboard.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Default: 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8787, help="Bind port. Default: 8787.")
    parser.add_argument(
        "--bridge-root",
        default=None,
        help="Optional Bridge root override. Defaults to the configured local Bridge path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run uvicorn for the local dashboard."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    bridge_root = Path(args.bridge_root) if args.bridge_root else default_config().bridge_root
    config = DashboardConfig(
        bridge_root=bridge_root,
        host=args.host,
        port=args.port,
    )
    import uvicorn

    uvicorn.run(create_app(config), host=args.host, port=args.port)
    return 0


app = create_app()


if __name__ == "__main__":
    raise SystemExit(main())

"""FastAPI app for the local AI Release Radar web dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from radar_web.config import DashboardConfig, default_config
from radar_web.manual_trigger import DailySimTrigger
from radar_web.models import ApiMessage, DashboardStatus
from radar_web.run_locator import find_latest_run, list_recent_runs, load_run_detail
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
    def api_status() -> dict[str, Any]:
        return build_status(dashboard_config).to_dict()

    @app.get("/api/runs")
    def api_runs(limit: int = 20) -> dict[str, Any]:
        bounded_limit = max(1, min(limit, 100))
        runs = list_recent_runs(dashboard_config.runs_root, limit=bounded_limit)
        return {
            "runs_root": str(dashboard_config.runs_root),
            "limit": bounded_limit,
            "runs": [run.to_dict() for run in runs],
        }

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
    if not config.runs_root.exists():
        warnings.append("runs_root_missing")
    return DashboardStatus(
        status=latest.get("status", "NO_DATA") if isinstance(latest, dict) else "NO_DATA",
        bridge_runs_root=str(config.runs_root),
        latest_run=latest,
        recent_run_count=len(recent_runs),
        scheduler=read_scheduler_status_placeholder(config),
        manual_trigger_enabled=True,
        warnings=tuple(sorted(set(warnings))),
    )


def read_scheduler_status_placeholder(config: DashboardConfig) -> dict[str, Any]:
    """Return read-only scheduler status for the configured task."""
    return read_scheduler_status(config.scheduler_task_name)


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
    if status == "PASS":
        return "status-pass"
    if status == "READY":
        return "status-pass"
    if status == "RUNNING":
        return "status-review"
    if status == "PASS_WITH_WARNINGS":
        return "status-warn"
    if status == "ACTION_REVIEW_REQUIRED":
        return "status-review"
    if status in {"HOLD", "HOLD_FOR_HUMAN_APPROVAL", "HUMAN_APPROVAL_REQUIRED"}:
        return "status-hold"
    if status in {"FAIL", "FAIL_STOP"}:
        return "status-fail"
    return "status-no-data"


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

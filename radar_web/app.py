"""FastAPI app for the local AI Release Radar web dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from radar_web.config import DashboardConfig, default_config
from radar_web.models import ApiMessage, DashboardStatus
from radar_web.run_locator import find_latest_run, list_recent_runs, load_run_detail


def create_app(config: DashboardConfig | None = None) -> FastAPI:
    """Create the local dashboard app."""
    dashboard_config = config or default_config()
    app = FastAPI(
        title="AI Release Radar Local Dashboard",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
    )
    app.state.dashboard_config = dashboard_config

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        status = build_status(dashboard_config).to_dict()
        latest = status.get("latest_run") or {}
        latest_run_id = latest.get("run_id", "NO_DATA") if isinstance(latest, dict) else "NO_DATA"
        latest_status = latest.get("status", "NO_DATA") if isinstance(latest, dict) else "NO_DATA"
        return (
            "<!doctype html><html><head><title>AI Release Radar</title></head>"
            "<body><h1>AI Release Radar</h1>"
            f"<p>Latest run: {latest_run_id}</p>"
            f"<p>Status: {latest_status}</p>"
            '<p><a href="/api/status">API status</a></p>'
            "</body></html>"
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

    return app


def build_status(config: DashboardConfig) -> DashboardStatus:
    """Build a top-level read-only dashboard status."""
    runs = list_recent_runs(config.runs_root, limit=20)
    latest = runs[0].to_dict() if runs else None
    warnings = list(config.validate_output_root())
    if not config.runs_root.exists():
        warnings.append("runs_root_missing")
    return DashboardStatus(
        status=latest.get("status", "NO_DATA") if isinstance(latest, dict) else "NO_DATA",
        bridge_runs_root=str(config.runs_root),
        latest_run=latest,
        recent_run_count=len(runs),
        scheduler=read_scheduler_status_placeholder(config),
        warnings=tuple(sorted(set(warnings))),
    )


def read_scheduler_status_placeholder(config: DashboardConfig) -> dict[str, Any]:
    """Return a safe placeholder until the scheduler reader is enabled."""
    return {
        "status": "NO_DATA",
        "task_name": config.scheduler_task_name,
        "read_only": True,
        "warnings": ["scheduler_status_reader_pending_0810"],
    }


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

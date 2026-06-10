"""Controlled manual daily-sim trigger for the local dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
import threading
from typing import Any, Callable

from radar_web.config import DashboardConfig


CompletedProcessRunner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class DailySimRunResult:
    """Serializable result for one controlled manual daily-sim attempt."""

    status: str
    command: list[str]
    output_root: str
    output_dir: str | None = None
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None
    automation_gate_status: str | None = None
    hag_status: str | None = None
    dashboard_updated: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "status": self.status,
            "manual_only": True,
            "command": list(self.command),
            "output_root": self.output_root,
            "output_dir": self.output_dir,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "warnings": list(self.warnings),
            "error": self.error,
            "writes_to_bridge": True,
            "automation_gate_status": self.automation_gate_status,
            "hag_status": self.hag_status,
            "dashboard_updated": self.dashboard_updated,
            "dashboard_refresh_recommended": True,
            "no_auto_action": True,
            "scheduler_triggered": False,
            "email_sent": False,
            "llm_called": False,
            "auto_action_executed": False,
            "other_repository_touched": False,
        }


class DailySimTrigger:
    """Synchronous local V1 trigger with lock and timeout."""

    def __init__(
        self,
        config: DashboardConfig,
        *,
        runner: CompletedProcessRunner = subprocess.run,
        lock: threading.Lock | None = None,
    ) -> None:
        self._config = config
        self._runner = runner
        self._lock = lock or threading.Lock()

    def run_now(self) -> DailySimRunResult:
        """Run the authorized daily-sim command once, or return already-running."""
        output_root = self._config.runs_root
        command = _daily_sim_command(output_root)
        if not self._lock.acquire(blocking=False):
            return DailySimRunResult(
                status="ALREADY_RUNNING",
                command=command,
                output_root=str(output_root),
                error="daily_sim_already_running",
            )
        try:
            validation_warnings = self._config.validate_output_root(output_root)
            if validation_warnings:
                return DailySimRunResult(
                    status="REFUSED",
                    command=command,
                    output_root=str(output_root),
                    warnings=tuple(validation_warnings),
                    error="invalid_output_root",
                )
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            completed = self._runner(
                command,
                cwd=str(self._config.repo_root),
                capture_output=True,
                text=True,
                timeout=self._config.daily_sim_timeout_seconds,
                env=env,
            )
            stdout = _to_text(completed.stdout)
            stderr = _to_text(completed.stderr)
            output_dir = _extract_output_dir(stdout)
            summary = _read_daily_sim_summary(output_dir)
            status = "PASS" if completed.returncode == 0 else "FAIL"
            return DailySimRunResult(
                status=status,
                command=command,
                output_root=str(output_root),
                output_dir=output_dir,
                return_code=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                warnings=tuple(summary["warnings"]),
                automation_gate_status=summary["automation_gate_status"],
                hag_status=summary["hag_status"],
                dashboard_updated=summary["dashboard_updated"],
            )
        except subprocess.TimeoutExpired as exc:
            return DailySimRunResult(
                status="TIMEOUT",
                command=command,
                output_root=str(output_root),
                stdout=_to_text(exc.stdout),
                stderr=_to_text(exc.stderr),
                warnings=("daily_sim_timeout",),
                error="daily_sim_timeout",
            )
        except OSError as exc:
            return DailySimRunResult(
                status="FAIL",
                command=command,
                output_root=str(output_root),
                warnings=(f"daily_sim_subprocess_error:{exc}",),
                error="daily_sim_subprocess_error",
            )
        finally:
            self._lock.release()


def _daily_sim_command(output_root: Path) -> list[str]:
    return [
        "python",
        "-m",
        "radar.cli",
        "daily-sim",
        "--output-root",
        str(output_root),
    ]


def _extract_output_dir(stdout: str) -> str | None:
    match = re.search(r"^Output dir:\s*(.+)$", stdout, flags=re.MULTILINE)
    if match is None:
        return None
    return match.group(1).strip()


def _read_daily_sim_summary(output_dir: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "automation_gate_status": None,
        "hag_status": None,
        "dashboard_updated": False,
        "warnings": [],
    }
    if output_dir is None:
        result["warnings"].append("daily_sim_output_dir_missing")
        return result
    run_dir = Path(output_dir)
    result["dashboard_updated"] = run_dir.is_dir()
    summary_path = run_dir / "0350-Daily_Sim_Summary.json"
    if not summary_path.exists():
        result["warnings"].append("daily_sim_summary_missing")
        return result
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["warnings"].append(f"daily_sim_summary_unreadable:{exc}")
        return result
    if not isinstance(data, dict):
        result["warnings"].append("daily_sim_summary_invalid")
        return result
    automation_gate = data.get("automation_gate")
    if not isinstance(automation_gate, dict):
        automation_gate = {}
    result["automation_gate_status"] = _string_or_none(
        data.get("automation_gate_status") or automation_gate.get("status")
    )
    result["hag_status"] = _string_or_none(data.get("hag_status"))
    return result


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _to_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)

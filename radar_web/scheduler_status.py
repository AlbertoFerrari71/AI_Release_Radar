"""Read-only Windows Task Scheduler status for the local dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import platform
import subprocess
from typing import Any, Callable


DEFAULT_TIMEOUT_SECONDS = 10


CompletedProcessRunner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class SchedulerStatus:
    """Serializable scheduler status card data."""

    status: str
    task_name: str
    read_only: bool = True
    task_path: str | None = None
    last_run_time: str | None = None
    last_task_result: int | None = None
    next_run_time: str | None = None
    number_of_missed_runs: int | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "status": self.status,
            "task_name": self.task_name,
            "read_only": self.read_only,
            "task_path": self.task_path,
            "last_run_time": self.last_run_time,
            "last_task_result": self.last_task_result,
            "next_run_time": self.next_run_time,
            "number_of_missed_runs": self.number_of_missed_runs,
            "warnings": list(self.warnings),
        }


def read_scheduler_status(
    task_name: str,
    *,
    runner: CompletedProcessRunner = subprocess.run,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Read a Windows scheduled task without modifying it."""
    if platform.system() != "Windows":
        return SchedulerStatus(
            status="NO_DATA",
            task_name=task_name,
            warnings=("scheduler_status_not_windows",),
        ).to_dict()
    command = _powershell_command(task_name)
    try:
        completed = runner(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                command,
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError:
        return SchedulerStatus(
            status="NO_DATA",
            task_name=task_name,
            warnings=("powershell_not_found",),
        ).to_dict()
    except subprocess.TimeoutExpired:
        return SchedulerStatus(
            status="NO_DATA",
            task_name=task_name,
            warnings=("scheduler_status_timeout",),
        ).to_dict()
    if completed.returncode != 0:
        warning = (completed.stderr or "scheduler_status_command_failed").strip()
        return SchedulerStatus(
            status="NO_DATA",
            task_name=task_name,
            warnings=(warning,),
        ).to_dict()
    raw = completed.stdout.strip()
    if not raw:
        return SchedulerStatus(
            status="NO_DATA",
            task_name=task_name,
            warnings=("scheduler_status_empty_output",),
        ).to_dict()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return SchedulerStatus(
            status="NO_DATA",
            task_name=task_name,
            warnings=(f"scheduler_status_invalid_json:{exc}",),
        ).to_dict()
    if not isinstance(data, dict):
        return SchedulerStatus(
            status="NO_DATA",
            task_name=task_name,
            warnings=("scheduler_status_invalid_payload",),
        ).to_dict()
    raw_warnings = data.get("warnings")
    warnings = raw_warnings if isinstance(raw_warnings, list) else []
    return SchedulerStatus(
        status=_string(data.get("status")),
        task_name=_string(data.get("task_name"), default=task_name),
        task_path=_optional_string(data.get("task_path")),
        last_run_time=_optional_string(data.get("last_run_time")),
        last_task_result=_optional_int(data.get("last_task_result")),
        next_run_time=_optional_string(data.get("next_run_time")),
        number_of_missed_runs=_optional_int(data.get("number_of_missed_runs")),
        warnings=tuple(str(item) for item in warnings),
    ).to_dict()


def _powershell_command(task_name: str) -> str:
    safe_task_name = task_name.replace("'", "''")
    return f"""
$taskName = '{safe_task_name}'
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($null -eq $task) {{
  [pscustomobject]@{{
    status = 'NO_DATA'
    task_name = $taskName
    read_only = $true
    warnings = @('scheduled_task_missing')
  }} | ConvertTo-Json -Compress
  exit 0
}}
$info = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
$lastRunTime = $null
$lastTaskResult = $null
$nextRunTime = $null
$numberOfMissedRuns = $null
if ($null -ne $info) {{
  $lastRunTime = $info.LastRunTime.ToString('o')
  $lastTaskResult = $info.LastTaskResult
  $nextRunTime = $info.NextRunTime.ToString('o')
  $numberOfMissedRuns = $info.NumberOfMissedRuns
}}
[pscustomobject]@{{
  status = [string] $task.State
  task_name = [string] $task.TaskName
  task_path = [string] $task.TaskPath
  last_run_time = $lastRunTime
  last_task_result = $lastTaskResult
  next_run_time = $nextRunTime
  number_of_missed_runs = $numberOfMissedRuns
  read_only = $true
  warnings = @()
}} | ConvertTo-Json -Compress
""".strip()


def _string(value: object, *, default: str = "NO_DATA") -> str:
    return value if isinstance(value, str) and value.strip() else default


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None

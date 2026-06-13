"""Configuration for the local AI Release Radar web dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
DEFAULT_BRIDGE_ROOT = Path(
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar"
)
DEFAULT_SCHEDULER_TASK_NAME = "AIReleaseRadar_DailyDryReport"
FORBIDDEN_PREFIXES = ("LAST-", "latest-")


@dataclass(frozen=True)
class DashboardConfig:
    """Runtime configuration for the local dashboard."""

    repo_root: Path = REPO_ROOT
    bridge_root: Path = DEFAULT_BRIDGE_ROOT
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    scheduler_task_name: str = DEFAULT_SCHEDULER_TASK_NAME
    daily_sim_timeout_seconds: int = 600

    @property
    def runs_root(self) -> Path:
        """Bridge root containing dated daily-sim run directories."""
        return self.bridge_root / "runs"

    @property
    def scheduler_logs_root(self) -> Path:
        """Bridge root containing scheduler logs."""
        return self.bridge_root / "scheduler_logs"

    @property
    def ui_preferences_path(self) -> Path:
        """Bridge-local UI preference file, intentionally outside the repository."""
        return self.bridge_root / "config" / "ui_preferences.ini"

    def validate_output_root(self, output_root: Path | None = None) -> list[str]:
        """Validate that an output root is outside the repo and not forbidden."""
        target = (output_root or self.runs_root).expanduser().resolve()
        warnings: list[str] = []
        if _is_path_within(target, self.repo_root.expanduser().resolve()):
            warnings.append("output_root_inside_repository")
        forbidden = [part for part in target.parts if part.startswith(FORBIDDEN_PREFIXES)]
        if forbidden:
            warnings.extend(f"forbidden_path_name:{part}" for part in forbidden)
        return warnings

    def validate_ui_preferences_path(self) -> list[str]:
        """Validate that UI preferences can only be written to the Bridge config file."""
        target = self.ui_preferences_path.expanduser().resolve()
        warnings: list[str] = []
        if _is_path_within(target, self.repo_root.expanduser().resolve()):
            warnings.append("ui_preferences_inside_repository")
        forbidden = [part for part in target.parts if part.startswith(FORBIDDEN_PREFIXES)]
        if forbidden:
            warnings.extend(f"forbidden_path_name:{part}" for part in forbidden)
        if target.name != "ui_preferences.ini":
            warnings.append("unexpected_ui_preferences_file")
        return warnings


def default_config() -> DashboardConfig:
    """Return the default local dashboard configuration."""
    return DashboardConfig()


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True

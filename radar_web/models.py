"""Serializable dashboard response models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DashboardStatus:
    """Top-level dashboard status returned by the API and UI."""

    status: str
    bridge_runs_root: str
    latest_run: dict[str, Any] | None
    recent_run_count: int
    scheduler: dict[str, Any]
    read_only_default: bool = True
    manual_trigger_enabled: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "status": self.status,
            "bridge_runs_root": self.bridge_runs_root,
            "latest_run": self.latest_run,
            "recent_run_count": self.recent_run_count,
            "scheduler": self.scheduler,
            "read_only_default": self.read_only_default,
            "manual_trigger_enabled": self.manual_trigger_enabled,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class ApiMessage:
    """Small serializable message for controlled error responses."""

    status: str
    message: str
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "status": self.status,
            "message": self.message,
            "warnings": list(self.warnings),
        }

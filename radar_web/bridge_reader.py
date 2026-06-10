"""Read-only helpers for AI Release Radar Bridge run artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


FORBIDDEN_PREFIXES = ("LAST-", "latest-")


@dataclass(frozen=True)
class ReadResult:
    """Serializable read result with warning-aware missing-file handling."""

    path: str
    exists: bool
    data: Any | None = None
    text: str | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "path": self.path,
            "exists": self.exists,
            "data": self.data,
            "text": self.text,
            "warnings": list(self.warnings),
        }


def load_json(path: str | Path) -> ReadResult:
    """Load JSON without writing anything; missing/invalid files become warnings."""
    target = Path(path)
    forbidden_warning = _forbidden_path_warning(target)
    if forbidden_warning is not None:
        return ReadResult(str(target), False, warnings=(forbidden_warning,))
    if not target.exists():
        return ReadResult(
            str(target),
            False,
            warnings=(f"missing_json:{target.name}",),
        )
    try:
        return ReadResult(
            str(target),
            True,
            data=json.loads(target.read_text(encoding="utf-8")),
        )
    except json.JSONDecodeError as exc:
        return ReadResult(
            str(target),
            True,
            warnings=(f"invalid_json:{target.name}:{exc}",),
        )
    except OSError as exc:
        return ReadResult(
            str(target),
            target.exists(),
            warnings=(f"read_error:{target.name}:{exc}",),
        )


def load_text(path: str | Path) -> ReadResult:
    """Load text without writing anything; missing files become warnings."""
    target = Path(path)
    forbidden_warning = _forbidden_path_warning(target)
    if forbidden_warning is not None:
        return ReadResult(str(target), False, warnings=(forbidden_warning,))
    if not target.exists():
        return ReadResult(
            str(target),
            False,
            warnings=(f"missing_text:{target.name}",),
        )
    try:
        return ReadResult(str(target), True, text=target.read_text(encoding="utf-8"))
    except OSError as exc:
        return ReadResult(
            str(target),
            target.exists(),
            warnings=(f"read_error:{target.name}:{exc}",),
        )


def load_run_summary(run_dir: str | Path) -> ReadResult:
    """Load the V1 real-run summary from a daily-sim run directory."""
    return load_json(Path(run_dir) / "0180-Run_Summary.json")


def load_daily_sim_summary(run_dir: str | Path) -> ReadResult:
    """Load the daily simulation summary from a daily-sim run directory."""
    return load_json(Path(run_dir) / "0350-Daily_Sim_Summary.json")


def load_gate_report(run_dir: str | Path) -> dict[str, Any]:
    """Load automation and daily quality gate artifacts from a run directory."""
    root = Path(run_dir)
    bundle = {
        "automation_gate_json": load_json(root / "0350-Daily_Sim_Gate.json"),
        "automation_gate_markdown": load_text(root / "0350-Daily_Sim_Gate.md"),
        "daily_quality_gate_v2_json": load_json(root / "0630-Daily_Quality_Gate_V2.json"),
        "daily_quality_gate_v2_markdown": load_text(root / "0630-Daily_Quality_Gate_V2.md"),
    }
    return _bundle_to_dict(bundle)


def load_hag_report(run_dir: str | Path) -> dict[str, Any]:
    """Load Human Approval Gate and prompt suggestion artifacts."""
    root = Path(run_dir)
    bundle = {
        "hag_markdown": load_text(root / "0680-Human_Approval_Gate_Report.md"),
        "prompt_suggestions_json": load_json(root / "0660-Codex_Prompt_Suggestions.json"),
        "prompt_suggestions_markdown": load_text(root / "0660-Codex_Prompt_Suggestions.md"),
    }
    return _bundle_to_dict(bundle)


def load_operator_dashboard(run_dir: str | Path) -> dict[str, Any]:
    """Load operator dashboard and supervised dry-run artifacts."""
    root = Path(run_dir)
    bundle = {
        "operator_dashboard_markdown": load_text(root / "0710-Daily_Operator_Dashboard.md"),
        "supervised_action_loop_dry_run": load_text(root / "0730-Supervised_Action_Loop_Dry_Run.md"),
        "action_triage_json": load_json(root / "0650-Action_Triage.json"),
    }
    return _bundle_to_dict(bundle)


def _bundle_to_dict(bundle: dict[str, ReadResult]) -> dict[str, Any]:
    warnings: list[str] = []
    result: dict[str, Any] = {}
    for key, read_result in bundle.items():
        result[key] = read_result.to_dict()
        warnings.extend(read_result.warnings)
    result["warnings"] = warnings
    return result


def _forbidden_path_warning(path: Path) -> str | None:
    for part in path.parts:
        if part.startswith(FORBIDDEN_PREFIXES):
            return f"forbidden_path_name:{part}"
    return None

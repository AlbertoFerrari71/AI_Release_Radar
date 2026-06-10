"""Append-only JSONL helpers for radar run indexes."""

from __future__ import annotations

import json
from pathlib import Path

from radar.hash_utils import stable_json_dumps
from radar.json_utils import ensure_parent_dir
from radar.models import RunIndexEntry


def _reject_forbidden_index_name(path: Path) -> None:
    name = path.name
    if name.startswith("LAST-") or name.startswith("latest-"):
        raise ValueError("Run index path must not use LAST-* or latest-* names.")


def append_run_index_entry(index_path: str | Path, entry: RunIndexEntry) -> None:
    """Append a single run entry as one JSONL line without rewriting the file."""
    if not isinstance(entry, RunIndexEntry):
        raise ValueError("entry must be a RunIndexEntry.")
    target = Path(index_path)
    _reject_forbidden_index_name(target)
    ensure_parent_dir(target)
    try:
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(stable_json_dumps(entry.to_dict()) + "\n")
    except OSError as exc:
        raise OSError(f"Unable to append run index entry to {target}: {exc}") from exc


def read_run_index(index_path: str | Path) -> list[RunIndexEntry]:
    """Read all valid run index entries from a JSONL file."""
    target = Path(index_path)
    _reject_forbidden_index_name(target)
    if not target.exists():
        return []

    entries: list[RunIndexEntry] = []
    try:
        with target.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    entries.append(RunIndexEntry.from_dict(json.loads(stripped)))
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    raise ValueError(
                        f"Invalid run index entry in {target} at line {line_number}: {exc}"
                    ) from exc
    except OSError as exc:
        raise OSError(f"Unable to read run index from {target}: {exc}") from exc
    return entries


def validate_run_index(index_path: str | Path) -> list[str]:
    """Return validation issues for a run index without rewriting it."""
    target = Path(index_path)
    _reject_forbidden_index_name(target)
    if not target.exists():
        return []

    issues: list[str] = []
    try:
        with target.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    RunIndexEntry.from_dict(json.loads(stripped))
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    issues.append(f"line {line_number}: {exc}")
    except OSError as exc:
        raise OSError(f"Unable to validate run index from {target}: {exc}") from exc
    return issues


def get_last_run_index_entry(index_path: str | Path) -> RunIndexEntry | None:
    """Return the last valid run index entry, or None for a missing/empty file."""
    target = Path(index_path)
    _reject_forbidden_index_name(target)
    if not target.exists():
        return None

    last_entry: RunIndexEntry | None = None
    try:
        with target.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    last_entry = RunIndexEntry.from_dict(json.loads(stripped))
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
    except OSError as exc:
        raise OSError(f"Unable to read run index from {target}: {exc}") from exc
    return last_entry

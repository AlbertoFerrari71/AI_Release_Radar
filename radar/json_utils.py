"""Deterministic JSON read/write helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_parent_dir(path: str | Path) -> None:
    """Create the parent directory for a target path when needed."""
    target = Path(path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Unable to create parent directory for {target}: {exc}") from exc


def _to_json_data(data: object) -> object:
    if hasattr(data, "to_dict") and callable(getattr(data, "to_dict")):
        return data.to_dict()
    if isinstance(data, list):
        return [_to_json_data(item) for item in data]
    if isinstance(data, tuple):
        return [_to_json_data(item) for item in data]
    if isinstance(data, dict):
        return {str(key): _to_json_data(value) for key, value in data.items()}
    return data


def write_json(path: str | Path, data: object) -> None:
    """Write JSON using UTF-8, sorted keys, stable indentation and LF newline."""
    target = Path(path)
    ensure_parent_dir(target)
    json_data = _to_json_data(data)
    try:
        text = json.dumps(json_data, ensure_ascii=False, indent=2, sort_keys=True)
        target.write_text(text + "\n", encoding="utf-8", newline="\n")
    except (TypeError, OSError) as exc:
        raise ValueError(f"Unable to write deterministic JSON to {target}: {exc}") from exc


def read_json(path: str | Path) -> Any:
    """Read UTF-8 JSON with a clear path-aware error."""
    target = Path(path)
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSON file not found: {target}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {target}: {exc}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read JSON from {target}: {exc}") from exc

"""Skill Invocation Ledger validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS: tuple[str, ...] = (
    "timestamp_utc",
    "project",
    "repo_path",
    "step_id",
    "process",
    "phase",
    "skill_name",
    "skill_path",
    "caller",
    "purpose",
    "input_scope",
    "output_scope",
    "result",
    "confidence",
    "notes",
)
VALID_RESULTS: tuple[str, ...] = (
    "used",
    "inspected_not_used",
    "skill_missing",
    "failed",
)


def validate_skill_invocation_record(record: object) -> dict[str, Any]:
    """Validate one Skill Invocation Ledger JSONL record."""
    if not isinstance(record, dict):
        raise ValueError("skill invocation record must be a dict.")
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise ValueError(f"missing required skill ledger fields: {', '.join(missing)}")
    result = record.get("result")
    if result not in VALID_RESULTS:
        raise ValueError(f"unsupported skill ledger result: {result}")
    confidence = record.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise ValueError("confidence must be a number.")
    if confidence < 0.0 or confidence > 1.0:
        raise ValueError("confidence must be between 0 and 1.")
    return dict(record)


def parse_skill_invocation_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Parse and validate a Skill Invocation Ledger JSONL file."""
    target = Path(path)
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
        records.append(validate_skill_invocation_record(data))
    return records

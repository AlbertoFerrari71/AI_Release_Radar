"""Source coverage diagnostic matrix helpers."""

from __future__ import annotations

from typing import Any


def build_source_coverage_matrix(source_diagnostics: object) -> list[dict[str, object]]:
    """Return an operator-readable source coverage matrix from diagnostics."""
    if not isinstance(source_diagnostics, list):
        return []
    matrix: list[dict[str, object]] = []
    for raw in source_diagnostics:
        if not isinstance(raw, dict):
            continue
        diagnostic_status = _string(raw.get("diagnostic_status"))
        manual_review = _bool(raw.get("manual_review_required"))
        row = {
            "source_id": _string(raw.get("source_id")),
            "provider": _string(raw.get("provider")),
            "priority": _string(raw.get("coverage_priority")),
            "fetch_status": _string(raw.get("fetch_status")),
            "parser_status": _string(raw.get("parser_status")),
            "http_status": _optional_int(raw.get("http_status_code")),
            "parsed_item_count": _int(raw.get("item_count")),
            "diagnostic_status": diagnostic_status,
            "unsupported_reason": _unsupported_reason(raw),
            "manual_review_required": manual_review,
            "scheduler_readiness_impact": _string(raw.get("scheduler_readiness")),
            "recommended_follow_up": _recommended_follow_up(raw),
            "machine_readable_alternative": _machine_readable_alternative(raw),
        }
        matrix.append(row)
    return matrix


def summarize_source_coverage_matrix(matrix: object) -> dict[str, object]:
    """Summarize source coverage matrix counts for reports and APIs."""
    rows = matrix if isinstance(matrix, list) else []
    summary = {
        "source_count": len(rows),
        "parsed_count": 0,
        "unsupported_source_count": 0,
        "manual_review_required_count": 0,
        "failed_count": 0,
        "hold_impact_count": 0,
        "warn_impact_count": 0,
        "ready_impact_count": 0,
        "coverage_warning": False,
    }
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        status = _string(raw.get("diagnostic_status"))
        readiness = _string(raw.get("scheduler_readiness_impact"))
        if status == "parsed":
            summary["parsed_count"] = int(summary["parsed_count"]) + 1
        if status == "fetched_but_unsupported":
            summary["unsupported_source_count"] = int(summary["unsupported_source_count"]) + 1
        if status in {"manual_review_required", "fetch_failed"}:
            summary["failed_count"] = int(summary["failed_count"]) + 1
        if raw.get("manual_review_required") is True:
            summary["manual_review_required_count"] = (
                int(summary["manual_review_required_count"]) + 1
            )
        if readiness == "hold":
            summary["hold_impact_count"] = int(summary["hold_impact_count"]) + 1
        elif readiness == "warn":
            summary["warn_impact_count"] = int(summary["warn_impact_count"]) + 1
        elif readiness == "ready":
            summary["ready_impact_count"] = int(summary["ready_impact_count"]) + 1
    source_count = int(summary["source_count"])
    parsed_count = int(summary["parsed_count"])
    summary["coverage_warning"] = bool(source_count and parsed_count / source_count < 0.50)
    return summary


def render_source_coverage_matrix_markdown(matrix: object) -> str:
    """Render the source coverage matrix as compact Markdown."""
    rows = matrix if isinstance(matrix, list) else []
    lines = [
        "| Fonte | Provider | Priorita | Fetch | Parser | HTTP | Item | Review | Readiness | Follow-up |",
        "|---|---|---:|---|---|---:|---:|---|---|---|",
    ]
    if not rows:
        lines.append("| none | none | none | none | none | none | 0 | none | none | none |")
        return "\n".join(lines)
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(raw.get("source_id")),
                    _md(raw.get("provider")),
                    _md(raw.get("priority")),
                    _md(raw.get("fetch_status")),
                    _md(raw.get("parser_status")),
                    _md(raw.get("http_status")),
                    _md(raw.get("parsed_item_count")),
                    _md(raw.get("manual_review_required")),
                    _md(raw.get("scheduler_readiness_impact")),
                    _md(raw.get("recommended_follow_up")),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _unsupported_reason(raw: dict[str, Any]) -> str:
    status = _string(raw.get("diagnostic_status"))
    if status == "parsed":
        return "none"
    for key in ("expected_failure_mode", "error_code", "error"):
        value = _string(raw.get(key))
        if value != "NO_DATA":
            return value
    return status


def _recommended_follow_up(raw: dict[str, Any]) -> str:
    for key in ("registry_recommended_follow_up", "recommended_follow_up"):
        value = _string(raw.get(key))
        if value != "NO_DATA":
            return value
    return "manual_review_source" if raw.get("manual_review_required") is True else "NO_DATA"


def _machine_readable_alternative(raw: dict[str, Any]) -> str:
    if raw.get("machine_readable_preferred") is True:
        follow_up = _string(raw.get("registry_recommended_follow_up"))
        if follow_up in {"evaluate_structured_endpoint", "prefer_machine_readable_alternative"}:
            return follow_up
        return "machine_readable_preferred"
    return "not_declared"


def _string(value: object) -> str:
    return value if isinstance(value, str) and value.strip() else "NO_DATA"


def _bool(value: object) -> bool:
    return value is True


def _int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _md(value: object) -> str:
    text = str(value if value is not None else "NO_DATA")
    return text.replace("|", "\\|").replace("\n", " ").strip()

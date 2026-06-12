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
            "machine_readable_preferred": _bool(raw.get("machine_readable_preferred")),
            "parser_strategy": _string(raw.get("parser_strategy")),
            "final_v1_status": _final_v1_status(raw, diagnostic_status),
            "final_v1_reason": _final_v1_reason(raw),
            "maintenance_backlog_category": _maintenance_backlog_category(raw),
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
        "final_classification_complete": True,
        "unsupported_explained_count": 0,
        "manual_review_explained_count": 0,
        "fragile_parser_count": 0,
        "http_403_count": 0,
    }
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        status = _string(raw.get("diagnostic_status"))
        readiness = _string(raw.get("scheduler_readiness_impact"))
        final_status = _string(raw.get("final_v1_status"))
        final_reason = _string(raw.get("final_v1_reason"))
        parser_strategy = _string(raw.get("parser_strategy"))
        if status == "parsed":
            summary["parsed_count"] = int(summary["parsed_count"]) + 1
        if status == "fetched_but_unsupported":
            summary["unsupported_source_count"] = int(summary["unsupported_source_count"]) + 1
            if final_reason != "NO_DATA":
                summary["unsupported_explained_count"] = (
                    int(summary["unsupported_explained_count"]) + 1
                )
        if status in {"manual_review_required", "fetch_failed"}:
            summary["failed_count"] = int(summary["failed_count"]) + 1
        if raw.get("manual_review_required") is True:
            summary["manual_review_required_count"] = (
                int(summary["manual_review_required_count"]) + 1
            )
            if final_reason != "NO_DATA":
                summary["manual_review_explained_count"] = (
                    int(summary["manual_review_explained_count"]) + 1
                )
        if raw.get("http_status") == 403:
            summary["http_403_count"] = int(summary["http_403_count"]) + 1
        if _is_fragile_parser(parser_strategy, status):
            summary["fragile_parser_count"] = int(summary["fragile_parser_count"]) + 1
        if final_status == "NO_DATA" or final_reason == "NO_DATA":
            summary["final_classification_complete"] = False
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


def evaluate_source_coverage_final_gate(
    matrix: object,
    *,
    parsed_count_target: int = 3,
) -> dict[str, object]:
    """Evaluate the V1 final source coverage gate from a matrix."""
    rows = matrix if isinstance(matrix, list) else []
    summary = summarize_source_coverage_matrix(rows)
    unsupported_count = int(summary["unsupported_source_count"])
    manual_review_count = int(summary["manual_review_required_count"])
    unsupported_unexplained = unsupported_count - int(summary["unsupported_explained_count"])
    manual_review_unexplained = manual_review_count - int(
        summary["manual_review_explained_count"]
    )
    parsed_count = int(summary["parsed_count"])
    fragile_parser_count = int(summary["fragile_parser_count"])
    blockers: list[str] = []
    warnings: list[str] = []

    if parsed_count < parsed_count_target:
        warnings.append(f"parsed_count_below_target:{parsed_count}/{parsed_count_target}")
    if unsupported_unexplained:
        blockers.append(f"unsupported_unexplained:{unsupported_unexplained}")
    if manual_review_unexplained:
        blockers.append(f"manual_review_unexplained:{manual_review_unexplained}")
    if fragile_parser_count:
        blockers.append(f"fragile_parser_count:{fragile_parser_count}")
    if summary["final_classification_complete"] is not True:
        blockers.append("final_classification_incomplete")
    if manual_review_count:
        warnings.append(f"manual_review_sources_present:{manual_review_count}")
    if unsupported_count:
        warnings.append(f"unsupported_sources_documented:{unsupported_count}")

    if blockers:
        status = "SOURCE_COVERAGE_FINAL_BLOCKED"
    elif parsed_count >= parsed_count_target and not warnings:
        status = "SOURCE_COVERAGE_FINAL_PASS"
    elif parsed_count >= parsed_count_target:
        status = "SOURCE_COVERAGE_FINAL_PASS_WITH_WARNINGS"
    else:
        status = "SOURCE_COVERAGE_FINAL_PASS_WITH_WARNINGS"

    return {
        "schema_version": 1,
        "gate": "1600) Source Coverage Closure Gate",
        "status": status,
        "source_count": summary["source_count"],
        "parsed_count": parsed_count,
        "parsed_count_target": parsed_count_target,
        "unsupported_count": unsupported_count,
        "unsupported_explained_count": summary["unsupported_explained_count"],
        "manual_review_count": manual_review_count,
        "manual_review_explained_count": summary["manual_review_explained_count"],
        "fragile_parser_count": fragile_parser_count,
        "http_403_count": summary["http_403_count"],
        "final_classification_complete": summary["final_classification_complete"],
        "blockers": blockers,
        "warnings": sorted(set(warnings)),
        "source_status_table": [
            {
                "source_id": _string(row.get("source_id")) if isinstance(row, dict) else "NO_DATA",
                "provider": _string(row.get("provider")) if isinstance(row, dict) else "NO_DATA",
                "priority": _string(row.get("priority")) if isinstance(row, dict) else "NO_DATA",
                "diagnostic_status": (
                    _string(row.get("diagnostic_status")) if isinstance(row, dict) else "NO_DATA"
                ),
                "parser_strategy": (
                    _string(row.get("parser_strategy")) if isinstance(row, dict) else "NO_DATA"
                ),
                "final_v1_status": (
                    _string(row.get("final_v1_status")) if isinstance(row, dict) else "NO_DATA"
                ),
                "final_v1_reason": (
                    _string(row.get("final_v1_reason")) if isinstance(row, dict) else "NO_DATA"
                ),
                "recommended_follow_up": (
                    _string(row.get("recommended_follow_up"))
                    if isinstance(row, dict)
                    else "NO_DATA"
                ),
                "maintenance_backlog_category": (
                    _string(row.get("maintenance_backlog_category"))
                    if isinstance(row, dict)
                    else "NO_DATA"
                ),
            }
            for row in rows
            if isinstance(row, dict)
        ],
    }


def render_source_coverage_final_gate_markdown(gate: dict[str, object]) -> str:
    """Render the final source coverage gate as Markdown."""
    lines = [
        "# 1600) Source Coverage Closure Gate",
        "",
        f"- [F] status: {gate.get('status')}.",
        f"- [F] source_count: {gate.get('source_count')}.",
        f"- [F] parsed_count: {gate.get('parsed_count')}.",
        f"- [F] parsed_count_target: {gate.get('parsed_count_target')}.",
        f"- [F] unsupported_count: {gate.get('unsupported_count')}.",
        f"- [F] unsupported_explained_count: {gate.get('unsupported_explained_count')}.",
        f"- [F] manual_review_count: {gate.get('manual_review_count')}.",
        f"- [F] manual_review_explained_count: {gate.get('manual_review_explained_count')}.",
        f"- [F] fragile_parser_count: {gate.get('fragile_parser_count')}.",
        f"- [F] 403_count: {gate.get('http_403_count')}.",
        f"- [F] final_classification_complete: {str(gate.get('final_classification_complete')).lower()}.",
        "",
        "## Blockers",
        "",
    ]
    blockers = _list(gate.get("blockers"))
    lines.extend(f"- [F] {item}" for item in blockers) if blockers else lines.append("- [F] none")
    lines.extend(["", "## Warnings", ""])
    warnings = _list(gate.get("warnings"))
    lines.extend(f"- [F] {item}" for item in warnings) if warnings else lines.append("- [F] none")
    lines.extend(
        [
            "",
            "## Source Status Table",
            "",
            "| Fonte | Provider | Priorita | Diagnostica | Parser | Stato V1 | Follow-up | Backlog |",
            "|---|---|---:|---|---|---|---|---|",
        ]
    )
    for raw in _list(gate.get("source_status_table")):
        if isinstance(raw, dict):
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md(raw.get("source_id")),
                        _md(raw.get("provider")),
                        _md(raw.get("priority")),
                        _md(raw.get("diagnostic_status")),
                        _md(raw.get("parser_strategy")),
                        _md(raw.get("final_v1_status")),
                        _md(raw.get("recommended_follow_up")),
                        _md(raw.get("maintenance_backlog_category")),
                    ]
                )
                + " |"
            )
    return "\n".join(lines).rstrip("\n") + "\n"


def render_source_coverage_matrix_markdown(matrix: object) -> str:
    """Render the source coverage matrix as compact Markdown."""
    rows = matrix if isinstance(matrix, list) else []
    lines = [
        (
            "| Fonte | Provider | Priorita | Fetch | Parser | HTTP | Item | Review | "
            "Readiness | Stato V1 | Follow-up |"
        ),
        "|---|---|---:|---|---|---:|---:|---|---|---|---|",
    ]
    if not rows:
        lines.append("| none | none | none | none | none | none | 0 | none | none | none | none |")
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
                    _md(raw.get("final_v1_status")),
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


def _final_v1_status(raw: dict[str, Any], diagnostic_status: str) -> str:
    value = _string(raw.get("final_v1_status"))
    if value != "NO_DATA":
        return value
    if diagnostic_status == "parsed":
        return "parsed"
    if raw.get("manual_review_required") is True:
        return "manual_review_403"
    if diagnostic_status == "fetched_but_unsupported":
        return "unsupported_documented"
    return "diagnostic_only"


def _final_v1_reason(raw: dict[str, Any]) -> str:
    value = _string(raw.get("final_v1_reason"))
    if value != "NO_DATA":
        return value
    failure_mode = _string(raw.get("expected_failure_mode"))
    follow_up = _recommended_follow_up(raw)
    if failure_mode != "NO_DATA":
        return f"{failure_mode}; follow_up={follow_up}"
    return f"follow_up={follow_up}"


def _maintenance_backlog_category(raw: dict[str, Any]) -> str:
    value = _string(raw.get("maintenance_backlog_category"))
    if value != "NO_DATA":
        return value
    if raw.get("manual_review_required") is True:
        return "manual_review"
    follow_up = _recommended_follow_up(raw)
    if follow_up == "prefer_machine_readable_alternative":
        return "source_replacement"
    if follow_up == "evaluate_structured_endpoint":
        return "parser_candidate"
    if follow_up == "use_parsed_items_after_gate":
        return "none"
    return "unsupported_policy"


def _is_fragile_parser(parser_strategy: str, diagnostic_status: str) -> bool:
    if diagnostic_status != "parsed":
        return False
    fragile_tokens = ("html_css", "browser", "headless", "scrape")
    return any(token in parser_strategy.lower() for token in fragile_tokens)


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


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []

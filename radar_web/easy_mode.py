"""Read-only Easy Mode payloads for the local dashboard."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from radar_web.run_locator import list_recent_runs, load_run_detail


ITALIAN_MONTHS = {
    1: "gennaio",
    2: "febbraio",
    3: "marzo",
    4: "aprile",
    5: "maggio",
    6: "giugno",
    7: "luglio",
    8: "agosto",
    9: "settembre",
    10: "ottobre",
    11: "novembre",
    12: "dicembre",
}

RED_STATUS_TOKENS = (
    "CRITICAL",
    "FAIL",
    "FAILED",
    "FAIL_STOP",
    "BLOCKED",
    "SOURCE_COVERAGE_FINAL_BLOCKED",
)
GRAY_STATUSES = {"NO_DATA", "MISSING", "RUNNING", "PARTIAL", "INCOMPLETE"}
HUMAN_APPROVAL_STATUSES = {
    "HOLD",
    "HOLD_FOR_HUMAN_APPROVAL",
    "HUMAN_APPROVAL_REQUIRED",
    "REQUIRES_HUMAN_APPROVAL",
}
YELLOW_STATUSES = {
    "ACTION_REVIEW_REQUIRED",
    "PASS_WITH_WARNINGS",
    "WARN",
    "WARNING",
    "NEEDS_REVIEW",
    "SUGGESTED_ONLY",
}

SEMAPHORE_LABELS = {
    "red": "Rosso",
    "yellow": "Giallo",
    "green": "Verde",
    "gray": "Grigio",
}

SEMAPHORE_MESSAGES = {
    "red": "Serve attenzione subito: ci sono elementi bloccanti o critici.",
    "yellow": "Ci sono novita o controlli da fare prima di decidere.",
    "green": "Nessuna novita importante rilevata.",
    "gray": "Dati insufficienti o run non completo.",
}


def build_easy_days(runs_root: str | Path, *, limit: int = 20) -> dict[str, Any]:
    """Build the chronological Easy Mode day list without writing anything."""
    bounded_limit = max(1, min(limit, 100))
    days = []
    for run in list_recent_runs(runs_root, limit=bounded_limit):
        detail = load_run_detail(runs_root, run.run_id)
        days.append(build_easy_day(detail if detail is not None else {"run": run.to_dict()}))
    return {
        "schema_version": 1,
        "mode": "easy",
        "language": "it",
        "runs_root": str(runs_root),
        "limit": bounded_limit,
        "count": len(days),
        "latest": days[0] if days else None,
        "days": days,
        "no_auto_action": True,
    }


def build_easy_latest(runs_root: str | Path) -> dict[str, Any]:
    """Return the latest Easy Mode day, or a deterministic NO_DATA payload."""
    days = build_easy_days(runs_root, limit=1)
    latest = days.get("latest")
    if isinstance(latest, dict):
        return latest
    return {
        "schema_version": 1,
        "run_id": None,
        "date_label": "Nessun giorno disponibile",
        "semaphore": "gray",
        "semaphore_label": SEMAPHORE_LABELS["gray"],
        "message": SEMAPHORE_MESSAGES["gray"],
        "important_count": 0,
        "monitor_count": 0,
        "source_warning_count": 0,
        "manual_review_count": 0,
        "action_count": 0,
        "detail_url": None,
        "expert_url": None,
    }


def build_easy_run_detail(runs_root: str | Path, run_id: str) -> dict[str, Any] | None:
    """Build one Easy Mode run detail payload without mutating Bridge data."""
    detail = load_run_detail(runs_root, run_id)
    if detail is None:
        return None
    day = build_easy_day(detail)
    cards = build_easy_cards(detail)
    source_warnings = build_easy_source_warnings(detail)
    return {
        "schema_version": 1,
        "mode": "easy",
        "language": "it",
        "day": day,
        "summary": _summary_for_day(day),
        "cards": cards,
        "cards_count": len(cards),
        "source_warnings": source_warnings,
        "source_warnings_count": len(source_warnings),
        "next_steps": _next_steps_for_day(day),
        "links": {
            "easy_home": "/",
            "expert_run": f"/runs/{day['run_id']}",
            "action_center": "/actions",
            "compact_report_api": f"/api/runs/{day['run_id']}/compact",
            "source_matrix_api": f"/api/runs/{day['run_id']}/source-matrix",
        },
        "no_auto_action": True,
    }


def build_easy_day(detail: dict[str, Any]) -> dict[str, Any]:
    """Build one list-row payload from an existing run detail or candidate dict."""
    run = _mapping(detail.get("run"))
    source_warnings = build_easy_source_warnings(detail)
    detail_warnings = sorted(
        {
            str(warning)
            for warning in _list(detail.get("warnings")) + _list(run.get("warnings"))
            if str(warning).strip()
        }
    )
    important_count = _important_count(detail, run)
    monitor_count = _int(run.get("monitor_only_action_count"))
    manual_review_count = max(
        _int(run.get("manual_review_queue_count")),
        len(_list(detail.get("manual_review_queue"))),
    )
    action_count = max(
        _int(run.get("direct_action_count")),
        len(_list(detail.get("direct_actions"))),
    )
    semaphore = calculate_easy_semaphore(
        {
            **run,
            "important_count": important_count,
            "monitor_count": monitor_count,
            "manual_review_count": manual_review_count,
            "source_warning_count": len(source_warnings),
            "warnings": detail_warnings,
        }
    )
    run_id = str(run.get("run_id") or "")
    return {
        "schema_version": 1,
        "run_id": run_id,
        "date_label": _date_label(run),
        "sort_key": str(run.get("sort_key") or ""),
        "semaphore": semaphore,
        "semaphore_label": SEMAPHORE_LABELS[semaphore],
        "message": SEMAPHORE_MESSAGES[semaphore],
        "important_count": important_count,
        "monitor_count": monitor_count,
        "source_warning_count": len(source_warnings),
        "manual_review_count": manual_review_count,
        "action_count": action_count,
        "prompt_suggestions_count": _int(run.get("prompt_suggestions_count")),
        "blocked_count": _int(run.get("blocked_action_count")),
        "status_label": _plain_status(run.get("status")),
        "detail_url": f"/easy/runs/{run_id}" if run_id else None,
        "expert_url": f"/runs/{run_id}" if run_id else None,
        "has_warnings": bool(detail_warnings or source_warnings),
    }


def calculate_easy_semaphore(day: dict[str, Any]) -> str:
    """Return red/yellow/green/gray from deterministic run signals."""
    statuses = [
        _code(day.get("status")),
        _code(day.get("automation_gate_status")),
        _code(day.get("daily_quality_gate_status")),
        _code(day.get("source_coverage_status")),
        _code(day.get("action_triage_status")),
        _code(day.get("hag_status")),
        _code(day.get("scheduler_readiness")),
        _code(day.get("prompt_suggestions_status")),
    ]
    blocked_count = _int(day.get("blocked_action_count") or day.get("blocked_count"))
    if any(_is_red_status(status) for status in statuses):
        return "red"
    if blocked_count > 0:
        return "red"
    if _code(day.get("hag_status")) in HUMAN_APPROVAL_STATUSES and (
        _int(day.get("important_count")) > 0 or _int(day.get("manual_review_count")) > 0
    ):
        return "red"
    if _has_insufficient_data(day, statuses):
        return "gray"
    if (
        _int(day.get("important_count")) > 0
        or _int(day.get("manual_review_count")) > 0
        or _int(day.get("source_warning_count")) > 0
        or _int(day.get("prompt_suggestions_count")) > 0
        or bool(_list(day.get("warnings")))
        or any(status in YELLOW_STATUSES for status in statuses)
    ):
        return "yellow"
    return "green"


def build_easy_cards(detail: dict[str, Any], *, limit: int = 12) -> list[dict[str, Any]]:
    """Build simple reading cards from existing structured run artifacts."""
    cards: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for action in (
        _list(detail.get("blocked_actions"))
        + _list(detail.get("direct_actions"))
        + _list(detail.get("manual_review_queue"))
        + _list(detail.get("monitor_only_summary"))
    ):
        item = _mapping(action)
        if not item:
            continue
        card = _card_from_action(item)
        key = (card["title"], card["source"])
        if key not in seen:
            cards.append(card)
            seen.add(key)
        if len(cards) >= limit:
            return cards

    for suggestion in _list(detail.get("prompt_suggestions")):
        item = _mapping(suggestion)
        if not item:
            continue
        card = {
            "kind": "suggestion",
            "title": _simple_title(item.get("title") or "Prompt suggerito"),
            "source": "Suggerimenti operativi",
            "importance": _importance_label(item.get("risk_class"), item.get("status")),
            "why_it_matters": "Esiste una bozza di istruzioni da valutare manualmente.",
            "what_to_do": "Apri l'Action Center e decidi se preparare il prompt.",
        }
        key = (card["title"], card["source"])
        if key not in seen:
            cards.append(card)
            seen.add(key)
        if len(cards) >= limit:
            return cards

    for source in build_easy_source_warnings(detail):
        card = {
            "kind": "source",
            "title": source["title"],
            "source": source["source"],
            "importance": source["importance"],
            "why_it_matters": source["why_it_matters"],
            "what_to_do": source["what_to_do"],
        }
        key = (card["title"], card["source"])
        if key not in seen:
            cards.append(card)
            seen.add(key)
        if len(cards) >= limit:
            return cards

    if cards:
        return cards
    day = build_easy_day(detail)
    if day["semaphore"] == "green":
        return [
            {
                "kind": "empty",
                "title": "Nessuna novita importante",
                "source": "Run giornaliero",
                "importance": "Bassa",
                "why_it_matters": "Il controllo non ha trovato elementi che richiedono lettura immediata.",
                "what_to_do": "Puoi archiviare mentalmente il giorno e controllare il prossimo run.",
            }
        ]
    return [
        {
            "kind": "missing",
            "title": "Dati non sufficienti",
            "source": "Run giornaliero",
            "importance": "Da verificare",
            "why_it_matters": "Alcuni file del run non sono disponibili o non sono leggibili.",
            "what_to_do": "Apri la vista Expert dello stesso run per controllare i dettagli tecnici.",
        }
    ]


def build_easy_source_warnings(detail: dict[str, Any], *, limit: int = 20) -> list[dict[str, Any]]:
    """Return operator-readable source warnings from the source matrix."""
    warnings: list[dict[str, Any]] = []
    for row in _list(detail.get("source_coverage_matrix")):
        source = _mapping(row)
        if not source or not _is_source_warning(source):
            continue
        warning = {
            "source": _plain_source(source.get("source_id")),
            "title": _source_warning_title(source),
            "importance": _source_importance(source),
            "why_it_matters": _source_why(source),
            "what_to_do": _source_next_step(source),
            "status": _plain_status(source.get("diagnostic_status")),
        }
        warnings.append(warning)
        if len(warnings) >= limit:
            break
    return warnings


def _card_from_action(item: dict[str, Any]) -> dict[str, Any]:
    triage_class = str(item.get("triage_class") or "")
    return {
        "kind": "action",
        "title": _simple_title(item.get("title") or item.get("source_id") or "Notizia da leggere"),
        "source": _plain_source(item.get("source_id") or item.get("target_project") or "Radar"),
        "importance": _importance_label(item.get("risk_class"), item.get("severity") or triage_class),
        "why_it_matters": _plain_reason(item.get("reason") or triage_class),
        "what_to_do": _next_step_for_action(triage_class),
    }


def _important_count(detail: dict[str, Any], run: dict[str, Any]) -> int:
    return max(
        _int(run.get("direct_action_count")),
        _int(run.get("blocked_action_count")),
        len(_list(detail.get("direct_actions"))),
        len(_list(detail.get("blocked_actions"))),
    )


def _summary_for_day(day: dict[str, Any]) -> str:
    if day["semaphore"] == "red":
        return (
            f"Il giorno contiene {day['important_count']} notizie importanti e "
            f"{day['source_warning_count']} fonti da controllare."
        )
    if day["semaphore"] == "yellow":
        return (
            f"Ci sono {day['important_count']} notizie importanti e "
            f"{day['monitor_count']} elementi da monitorare."
        )
    if day["semaphore"] == "green":
        return "Non risultano novita importanti per questo run."
    return "Il run non contiene abbastanza dati leggibili per una sintesi affidabile."


def _next_steps_for_day(day: dict[str, Any]) -> list[str]:
    if day["semaphore"] == "red":
        return [
            "Leggi le card principali.",
            "Apri l'Action Center prima di decidere qualsiasi azione.",
            "Controlla le fonti segnalate se una decisione dipende dalla copertura.",
        ]
    if day["semaphore"] == "yellow":
        return [
            "Leggi le novita principali.",
            "Tieni monitorati gli elementi non urgenti.",
            "Usa la vista Expert solo se serve capire il dettaglio tecnico.",
        ]
    if day["semaphore"] == "green":
        return ["Nessuna azione immediata.", "Puoi passare al giorno successivo."]
    return ["Apri la vista Expert per verificare quali dati mancano."]


def _date_label(run: dict[str, Any]) -> str:
    sort_key = str(run.get("sort_key") or "").replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(sort_key)
    except ValueError:
        return str(run.get("run_id") or "Giorno non disponibile")
    month = ITALIAN_MONTHS.get(parsed.month, f"mese {parsed.month}")
    return f"{parsed.day} {month} {parsed.year}, {parsed:%H:%M}"


def _has_insufficient_data(day: dict[str, Any], statuses: list[str]) -> bool:
    warnings = _list(day.get("warnings"))
    if any(
        str(warning).startswith(("missing_json:", "invalid_json:", "read_error:", "runs_root_"))
        for warning in warnings
    ):
        return True
    if _code(day.get("status")) in GRAY_STATUSES and not (
        _int(day.get("important_count"))
        or _int(day.get("monitor_count"))
        or _int(day.get("manual_review_count"))
        or _int(day.get("source_warning_count"))
    ):
        return True
    return all(status in GRAY_STATUSES for status in statuses if status)


def _is_red_status(status: str) -> bool:
    return any(token in status for token in RED_STATUS_TOKENS)


def _is_source_warning(source: dict[str, Any]) -> bool:
    diagnostic = _code(source.get("diagnostic_status"))
    readiness = _code(source.get("scheduler_readiness_impact"))
    final_status = _code(source.get("final_v1_status"))
    return (
        source.get("manual_review_required") is True
        or source.get("http_status") == 403
        or diagnostic in {"FETCH_FAILED", "MANUAL_REVIEW_REQUIRED", "FETCHED_BUT_UNSUPPORTED"}
        or readiness in {"HOLD", "WARN"}
        or "UNSUPPORTED" in final_status
    )


def _source_warning_title(source: dict[str, Any]) -> str:
    if source.get("http_status") == 403:
        return "Fonte da controllare manualmente"
    if source.get("manual_review_required") is True:
        return "Fonte da controllare manualmente"
    if _code(source.get("diagnostic_status")) == "FETCHED_BUT_UNSUPPORTED":
        return "Fonte non gestita automaticamente"
    if _code(source.get("diagnostic_status")) == "FETCH_FAILED":
        return "Fonte non letta"
    return "Fonte con avviso"


def _source_importance(source: dict[str, Any]) -> str:
    if source.get("http_status") == 403 or source.get("manual_review_required") is True:
        return "Alta"
    if _code(source.get("scheduler_readiness_impact")) == "HOLD":
        return "Alta"
    return "Media"


def _source_why(source: dict[str, Any]) -> str:
    if source.get("http_status") == 403:
        return "La fonte non e accessibile automaticamente e puo richiedere controllo manuale."
    if source.get("manual_review_required") is True:
        return "Il sistema segnala che la fonte va verificata da una persona."
    if _code(source.get("diagnostic_status")) == "FETCHED_BUT_UNSUPPORTED":
        return "La fonte risponde, ma il lettore automatico non la gestisce in modo completo."
    if _code(source.get("diagnostic_status")) == "FETCH_FAILED":
        return "La fonte non e stata letta correttamente."
    return "La fonte incide sulla qualita della lettura giornaliera."


def _source_next_step(source: dict[str, Any]) -> str:
    follow_up = _code(source.get("recommended_follow_up"))
    if "MANUAL" in follow_up or source.get("manual_review_required") is True:
        return "Controlla manualmente la fonte prima di decidere."
    if "STRUCTURED" in follow_up:
        return "Valuta in futuro una fonte strutturata piu affidabile."
    return "Tieni la fonte in monitoraggio e continua dal flusso manuale."


def _simple_title(value: object) -> str:
    text = str(value or "").strip() or "Notizia da leggere"
    replacements = {
        "Aggregate direct actions": "Notizie importanti aggregate",
        "Aggregate monitor-only actions": "Notizie da monitorare aggregate",
        "Prompt suggestion": "Prompt suggerito",
        "Manual review: ": "Controllo manuale: ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    cleaned = _clean_easy_text(text)
    return _humanize_identifier(cleaned) if _looks_like_identifier(cleaned) else cleaned


def _plain_source(value: object) -> str:
    text = str(value or "").strip() or "Fonte non indicata"
    mapping = {
        "Radar source coverage": "Copertura fonti Radar",
        "Mixed project targets": "Piu progetti",
        "Ambiguous project": "Progetto da chiarire",
    }
    cleaned = _clean_easy_text(mapping.get(text, text))
    return _humanize_identifier(cleaned) if _looks_like_identifier(cleaned) else cleaned


def _importance_label(risk: object, severity: object) -> str:
    text = f"{risk or ''} {severity or ''}".upper()
    if "HIGH" in text or "BLOCKED" in text or "MANUAL" in text or "L2" in text:
        return "Alta"
    if "MEDIUM" in text or "MONITOR" in text:
        return "Media"
    if "LOW" in text:
        return "Bassa"
    return "Media"


def _plain_reason(value: object) -> str:
    text = str(value or "").strip()
    mapping = {
        "direct actions exist, but source coverage is below full-pass threshold": (
            "Ci sono contenuti potenzialmente rilevanti, ma la copertura delle fonti non basta "
            "per procedere senza controllo."
        ),
        "direct_actions_present": "Ci sono novita da leggere prima di decidere.",
        "fetched_but_unsupported": "La fonte risponde ma non e gestita automaticamente.",
        "blocked_by_coverage": "La decisione e bloccata dalla copertura delle fonti.",
        "blocked_by_manual_review": "La decisione richiede un controllo manuale.",
        "manual_review": "Serve un controllo manuale.",
        "manual_review_required": "Serve un controllo manuale.",
        "monitor": "Elemento utile da tenere sotto osservazione.",
    }
    return _clean_easy_text(mapping.get(text, text.replace("_", " ") or "Segnale rilevante."))


def _next_step_for_action(triage_class: str) -> str:
    code = _code(triage_class)
    if "BLOCKED" in code:
        return "Apri l'Action Center e decidi il prossimo passaggio manuale."
    if "MANUAL_REVIEW" in code:
        return "Controlla la fonte e poi torna all'Action Center."
    if "MONITOR" in code:
        return "Tieni monitorato, senza azione immediata."
    if "PROMPT" in code:
        return "Valuta il prompt suggerito, senza eseguirlo automaticamente."
    return "Leggi la card e prosegui nel flusso manuale."


def _plain_status(value: object) -> str:
    status = _code(value)
    mapping = {
        "NO_DATA": "Dati non disponibili",
        "PASS": "Tutto ok",
        "PASS_WITH_WARNINGS": "Ok con avvisi",
        "ACTION_REVIEW_REQUIRED": "Da controllare",
        "CRITICAL": "Critico",
        "HOLD": "In attesa",
        "HOLD_FOR_HUMAN_APPROVAL": "Serve approvazione umana",
        "HUMAN_APPROVAL_REQUIRED": "Serve approvazione umana",
        "SUGGESTED_ONLY": "Suggerito, non eseguito",
        "WARN": "Avviso",
        "WARNING": "Avviso",
    }
    return mapping.get(status, _clean_easy_text(status.replace("_", " ").title()))


def _clean_easy_text(value: str) -> str:
    text = value.replace("HAG", "Serve approvazione umana")
    text = text.replace("manual review", "controllo manuale")
    text = text.replace("Manual review", "Controllo manuale")
    text = text.replace("unsupported", "non gestita automaticamente")
    text = text.replace("Unsupported", "Non gestita automaticamente")
    text = text.replace("parser", "lettore automatico")
    text = text.replace("Parser", "Lettore automatico")
    return text


def _looks_like_identifier(value: str) -> bool:
    return "_" in value or value.islower()


def _humanize_identifier(value: str) -> str:
    words = value.replace("-", " ").replace("_", " ").split()
    if not words:
        return value
    token_map = {
        "api": "API",
        "cli": "CLI",
        "codex": "Codex",
        "github": "GitHub",
        "md": "documentazione",
        "openai": "OpenAI",
    }
    humanized = [token_map.get(word.lower(), word.capitalize()) for word in words]
    return " ".join(humanized)


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _code(value: object) -> str:
    return str(value or "NO_DATA").strip().upper()

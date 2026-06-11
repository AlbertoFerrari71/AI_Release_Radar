"""Bridge-only dynamic news translation cache and QA helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from radar.json_utils import read_json, write_json


SUPPORTED_TRANSLATION_LOCALES = ("en", "it", "fr", "de", "es")
DEFAULT_SOURCE_LOCALE = "en"
TRANSLATION_STATUSES = ("translated", "missing", "needs_review", "failed")
TRANSLATION_MODEL_PROFILES = ("cheap", "balanced", "quality")
DEFAULT_TRANSLATION_PROFILE = "balanced"
FORBIDDEN_PREFIXES = ("LAST-", "latest-")

_LINK_RE = re.compile(r"https?://[^\s)>\]\"']+")
_VERSION_RE = re.compile(r"\bv?\d+(?:\.\d+){1,4}(?:[-+][A-Za-z0-9.]+)?\b")
_PATH_RE = re.compile(
    r"(?:[A-Za-z]:\\[^\s]+|/[A-Za-z0-9._/-]+|\b[\w.-]+(?:/|\\)[\w./\\-]+)"
)
_COMMAND_RE = re.compile(
    r"\b(?:python|pip|git|gh|npm|uvicorn|powershell(?:\.exe)?|cmd(?:\.exe)?)\b[^\n.;]*"
)


def normalize_translation_locale(value: object) -> str:
    """Normalize a translation locale with EN fallback."""
    if not isinstance(value, str):
        return DEFAULT_SOURCE_LOCALE
    text = value.strip().lower().replace("_", "-")
    language = text.split("-", 1)[0] if text else DEFAULT_SOURCE_LOCALE
    return language if language in SUPPORTED_TRANSLATION_LOCALES else DEFAULT_SOURCE_LOCALE


def translation_run_root(run_id: str, bridge_root: str | Path) -> Path:
    """Return the Bridge translation run root for one run id."""
    clean_run_id = _safe_run_id(run_id)
    root = Path(bridge_root) / "translations" / clean_run_id
    if _has_forbidden_path_part(root):
        raise ValueError(f"forbidden translation path: {root}")
    return root


def translation_cache_path(run_id: str, locale: object, bridge_root: str | Path) -> Path:
    """Return the cache file path for one run and locale."""
    normalized_locale = normalize_translation_locale(locale)
    return translation_run_root(run_id, bridge_root) / f"translated_items.{normalized_locale}.json"


def load_translation_cache(
    run_id: str,
    locale: object,
    bridge_root: str | Path,
) -> list[dict[str, Any]]:
    """Load a Bridge translation cache; missing or invalid files return an empty list."""
    path = translation_cache_path(run_id, locale, bridge_root)
    if not path.exists():
        return []
    try:
        raw = read_json(path)
    except (FileNotFoundError, OSError, ValueError):
        return []
    if isinstance(raw, dict):
        values = raw.get("items", [])
    else:
        values = raw
    if not isinstance(values, list):
        return []
    target_locale = normalize_translation_locale(locale)
    return [
        normalize_translation_item(item, run_id=run_id, target_locale=target_locale)
        for item in values
        if isinstance(item, dict)
    ]


def save_translation_cache(
    run_id: str,
    locale: object,
    items: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    bridge_root: str | Path,
) -> Path:
    """Write translated items into the Bridge cache and update the run index/report."""
    target_locale = normalize_translation_locale(locale)
    root = translation_run_root(run_id, bridge_root)
    path = root / f"translated_items.{target_locale}.json"
    normalized_items = [
        normalize_translation_item(item, run_id=run_id, target_locale=target_locale)
        for item in items
    ]
    write_json(path, normalized_items)
    _write_translation_index(run_id, bridge_root)
    _write_translation_report(run_id, bridge_root)
    return path


def translation_cache_status(
    run_id: str,
    locales: list[str] | tuple[str, ...],
    bridge_root: str | Path,
) -> dict[str, Any]:
    """Return per-locale cache status without creating any files."""
    result: dict[str, Any] = {"run_id": run_id, "locales": {}, "warnings": []}
    for locale in locales:
        normalized_locale = normalize_translation_locale(locale)
        path = translation_cache_path(run_id, normalized_locale, bridge_root)
        items = load_translation_cache(run_id, normalized_locale, bridge_root)
        result["locales"][normalized_locale] = {
            "path": str(path),
            "exists": path.exists(),
            "item_count": len(items),
            "status": "cached" if items else "missing",
        }
    return result


def normalize_translation_item(
    item: dict[str, Any],
    *,
    run_id: str,
    target_locale: str,
) -> dict[str, Any]:
    """Normalize one translated item into the stable Bridge schema."""
    status = str(item.get("translation_status") or "translated").strip().lower()
    if status not in TRANSLATION_STATUSES:
        status = "needs_review"
    profile = str(item.get("translation_model_profile") or DEFAULT_TRANSLATION_PROFILE).strip().lower()
    if profile not in TRANSLATION_MODEL_PROFILES:
        profile = DEFAULT_TRANSLATION_PROFILE
    review_required = bool(item.get("review_required")) or status in {"needs_review", "failed"}
    return {
        "run_id": str(item.get("run_id") or run_id),
        "source_item_id": str(item.get("source_item_id") or ""),
        "target_locale": normalize_translation_locale(item.get("target_locale") or target_locale),
        "source_locale": normalize_translation_locale(item.get("source_locale") or DEFAULT_SOURCE_LOCALE),
        "title_translated": str(item.get("title_translated") or ""),
        "summary_translated": str(item.get("summary_translated") or ""),
        "technical_terms_preserved": bool(item.get("technical_terms_preserved", True)),
        "links_preserved": bool(item.get("links_preserved", True)),
        "version_numbers_preserved": bool(item.get("version_numbers_preserved", True)),
        "translation_model_profile": profile,
        "translation_status": status,
        "review_required": review_required,
        "created_at": str(item.get("created_at") or utc_now()),
    }


def validate_translation_item(item: dict[str, Any]) -> list[str]:
    """Return schema warnings for one normalized translation item."""
    warnings: list[str] = []
    required = {
        "run_id",
        "source_item_id",
        "target_locale",
        "source_locale",
        "title_translated",
        "summary_translated",
        "technical_terms_preserved",
        "links_preserved",
        "version_numbers_preserved",
        "translation_model_profile",
        "translation_status",
        "review_required",
        "created_at",
    }
    missing = sorted(key for key in required if key not in item)
    warnings.extend(f"missing_field:{key}" for key in missing)
    status = str(item.get("translation_status") or "")
    if status and status not in TRANSLATION_STATUSES:
        warnings.append(f"unsupported_translation_status:{status}")
    locale = str(item.get("target_locale") or "")
    if locale and locale not in SUPPORTED_TRANSLATION_LOCALES:
        warnings.append(f"unsupported_target_locale:{locale}")
    profile = str(item.get("translation_model_profile") or "")
    if profile and profile not in TRANSLATION_MODEL_PROFILES:
        warnings.append(f"unsupported_translation_model_profile:{profile}")
    return warnings


def apply_translation_cache_to_actions(
    actions: list[dict[str, Any]],
    *,
    run_id: str | None,
    locale: object,
    bridge_root: str | Path,
) -> list[dict[str, Any]]:
    """Attach cached translation display fields to Action Center action dictionaries."""
    target_locale = normalize_translation_locale(locale)
    if not run_id:
        cache: list[dict[str, Any]] = []
    else:
        cache = load_translation_cache(run_id, target_locale, bridge_root)
    by_source_item_id = {
        item["source_item_id"]: item
        for item in cache
        if item.get("source_item_id")
    }
    localized: list[dict[str, Any]] = []
    for action in actions:
        source_item_id = str(action.get("source_item_id") or "")
        cached = by_source_item_id.get(source_item_id)
        item = dict(action)
        item["source_title"] = item.get("title") or ""
        item["source_summary"] = item.get("summary") or ""
        if cached and cached["translation_status"] in {"translated", "needs_review"}:
            item["localized_title"] = cached["title_translated"] or item["source_title"]
            item["localized_summary"] = cached["summary_translated"] or item["source_summary"]
            badge = "needs_review" if cached["review_required"] else "cached"
            status = cached["translation_status"]
        elif target_locale == DEFAULT_SOURCE_LOCALE:
            item["localized_title"] = item["source_title"]
            item["localized_summary"] = item["source_summary"]
            badge = "source"
            status = "source"
        else:
            item["localized_title"] = item["source_title"]
            item["localized_summary"] = item["source_summary"]
            badge = "missing"
            status = "missing"
        item["translation"] = {
            "target_locale": target_locale,
            "status": status,
            "badge": badge,
            "review_required": bool(cached and cached.get("review_required")),
            "source_item_id": source_item_id,
        }
        localized.append(item)
    return localized


def extract_links(value: str) -> set[str]:
    """Extract links that must be preserved across translations."""
    return set(_LINK_RE.findall(value or ""))


def extract_version_numbers(value: str) -> set[str]:
    """Extract version-like tokens that must be preserved across translations."""
    return set(_VERSION_RE.findall(value or ""))


def extract_paths(value: str) -> set[str]:
    """Extract path-like tokens that must not be translated."""
    return set(_PATH_RE.findall(value or ""))


def extract_commands(value: str) -> set[str]:
    """Extract CLI command snippets that must not be translated."""
    return {command.strip() for command in _COMMAND_RE.findall(value or "")}


def preservation_report(source: str, translated: str) -> dict[str, Any]:
    """Return deterministic preservation checks for one source/translation pair."""
    source_text = source or ""
    translated_text = translated or ""
    checks = {
        "links_preserved": _is_subset(extract_links(source_text), extract_links(translated_text)),
        "version_numbers_preserved": _is_subset(
            extract_version_numbers(source_text),
            extract_version_numbers(translated_text),
        ),
        "paths_preserved": _is_subset(extract_paths(source_text), extract_paths(translated_text)),
        "commands_preserved": _is_subset(
            extract_commands(source_text),
            extract_commands(translated_text),
        ),
    }
    checks["preservation_pass"] = all(checks.values())
    return checks


def utc_now() -> str:
    """Return a stable UTC timestamp for translation cache records."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_translation_index(run_id: str, bridge_root: str | Path) -> None:
    root = translation_run_root(run_id, bridge_root)
    locales: dict[str, Any] = {}
    for locale in SUPPORTED_TRANSLATION_LOCALES:
        path = root / f"translated_items.{locale}.json"
        items = load_translation_cache(run_id, locale, bridge_root) if path.exists() else []
        locales[locale] = {
            "path": str(path),
            "exists": path.exists(),
            "item_count": len(items),
            "status": "cached" if items else "missing",
        }
    write_json(
        root / "translation_index.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "locales": locales,
            "no_runtime_llm": True,
            "bridge_only": True,
            "updated_at": utc_now(),
        },
    )


def _write_translation_report(run_id: str, bridge_root: str | Path) -> None:
    status = translation_cache_status(run_id, SUPPORTED_TRANSLATION_LOCALES, bridge_root)
    lines = [
        "# Translation Cache Report",
        "",
        f"- [F] run_id: {run_id}.",
        "- [F] output_scope: Bridge-only.",
        "- [F] runtime_llm_call: false.",
        "",
        "## Locale Status",
        "",
    ]
    for locale, info in status["locales"].items():
        lines.append(
            f"- [F] {locale}: {info['status']} ({info['item_count']} items) -> {info['path']}."
        )
    path = translation_run_root(run_id, bridge_root) / "translation_report.md"
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def _safe_run_id(run_id: str) -> str:
    text = str(run_id or "").strip()
    if not text:
        raise ValueError("run_id is required")
    if any(separator in text for separator in ("/", "\\")):
        raise ValueError(f"unsafe run_id: {text}")
    return text


def _has_forbidden_path_part(path: Path) -> bool:
    return any(part.startswith(FORBIDDEN_PREFIXES) for part in path.parts)


def _is_subset(expected: set[str], observed: set[str]) -> bool:
    return expected.issubset(observed)

"""Deterministic UI internationalization helpers for the local dashboard."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any


SUPPORTED_LOCALES = ["en", "it", "fr", "de", "es"]
DEFAULT_LOCALE = "en"

_CATALOG_DIR = Path(__file__).resolve().parent / "locales"
_CATALOG_CACHE: dict[str, dict[str, str]] = {}


def normalize_locale(value: object) -> str:
    """Return a supported locale code, falling back to English."""
    if not isinstance(value, str):
        return DEFAULT_LOCALE
    text = value.strip().lower().replace("_", "-")
    if not text:
        return DEFAULT_LOCALE
    language = text.split("-", 1)[0]
    return language if language in SUPPORTED_LOCALES else DEFAULT_LOCALE


def load_catalog(locale: object) -> dict[str, str]:
    """Load one locale catalog from radar_web/locales with in-memory caching."""
    normalized = normalize_locale(locale)
    if normalized in _CATALOG_CACHE:
        return dict(_CATALOG_CACHE[normalized])
    path = _CATALOG_DIR / f"{normalized}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        data = {}
    catalog = {str(key): str(value) for key, value in data.items()}
    _CATALOG_CACHE[normalized] = catalog
    return dict(catalog)


def translate(key: str, locale: object, **kwargs: object) -> str:
    """Translate one UI key with fallback to EN and a visible missing marker."""
    text_key = str(key)
    catalog = load_catalog(locale)
    default_catalog = load_catalog(DEFAULT_LOCALE)
    template = catalog.get(text_key, default_catalog.get(text_key, f"[missing:{text_key}]"))
    if not kwargs:
        return template
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return template


def catalog_keys(locale: object) -> set[str]:
    """Return all keys available in one normalized locale catalog."""
    return set(load_catalog(locale).keys())


def missing_keys(locale: object) -> set[str]:
    """Return EN keys missing from one locale catalog."""
    return catalog_keys(DEFAULT_LOCALE) - catalog_keys(locale)


def all_catalog_diagnostics() -> dict[str, Any]:
    """Return deterministic diagnostics for all supported locale catalogs."""
    base_keys = catalog_keys(DEFAULT_LOCALE)
    diagnostics: dict[str, Any] = {}
    for locale in SUPPORTED_LOCALES:
        keys = catalog_keys(locale)
        diagnostics[locale] = {
            "key_count": len(keys),
            "missing_keys": sorted(base_keys - keys),
            "extra_keys": sorted(keys - base_keys),
        }
    return diagnostics


def format_datetime_for_locale(value: object, locale: object) -> str:
    """Format ISO-like datetimes for supported dashboard locales."""
    if value is None:
        return translate("status_label.no_data", locale)
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if not text or text.upper() == "NO_DATA":
            return translate("status_label.no_data", locale)
        normalized = text.replace("Z", "+00:00")
        normalized = re.sub(r"(\.\d{6})\d+([+-]\d{2}:\d{2})$", r"\1\2", normalized)
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return text
    locale_code = normalize_locale(locale)
    if locale_code == "en":
        return parsed.strftime("%Y-%m-%d %H:%M")
    if locale_code == "de":
        return parsed.strftime("%d.%m.%Y %H:%M")
    return parsed.strftime("%d/%m/%Y %H:%M")


def format_status_for_locale(status: object, locale: object) -> str:
    """Return a localized label for common technical status values."""
    if status is None:
        return translate("status_label.no_data", locale)
    text = str(status).strip()
    if not text:
        return translate("status_label.no_data", locale)
    status_key = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    label = translate(f"status_label.{status_key}", locale)
    return text if label.startswith("[missing:") else label


def format_catalog_value_for_locale(prefix: str, value: object, locale: object) -> str:
    """Return a localized catalog label for a stable internal code."""
    if value is None:
        return translate("status_label.no_data", locale)
    text = str(value).strip()
    if not text:
        return translate("status_label.no_data", locale)
    value_key = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    label = translate(f"{prefix}.{value_key}", locale)
    return text if label.startswith("[missing:") else label


def format_bool_for_locale(value: object, locale: object) -> str:
    """Render booleans with a localized Yes/No label."""
    if isinstance(value, bool):
        return translate("bool.yes" if value else "bool.no", locale)
    if value is None:
        return translate("status_label.no_data", locale)
    return str(value)

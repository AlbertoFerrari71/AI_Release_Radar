"""Local UI preference handling for the AI Release Radar dashboard."""

from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from typing import Any

from radar_web.config import DashboardConfig
from radar_web.i18n import SUPPORTED_LOCALES


DEFAULT_LANGUAGE = "auto"
DEFAULT_START_MODE = "easy"
DEFAULT_LAST_SELECTED_LANGUAGE = "it"
DEFAULT_LAST_SELECTED_MODE = "easy"
SUPPORTED_LANGUAGE_VALUES = tuple(["auto", *SUPPORTED_LOCALES])
SUPPORTED_MODES = ("easy", "expert")
ALLOWED_POST_FIELDS = {
    "language",
    "start_mode",
    "last_selected_language",
    "last_selected_mode",
}


@dataclass(frozen=True)
class UIPreferences:
    """Operator UI preferences persisted outside the repository."""

    language: str = DEFAULT_LANGUAGE
    start_mode: str = DEFAULT_START_MODE
    last_selected_language: str = DEFAULT_LAST_SELECTED_LANGUAGE
    last_selected_mode: str = DEFAULT_LAST_SELECTED_MODE

    def to_dict(self) -> dict[str, str]:
        return {
            "language": self.language,
            "start_mode": self.start_mode,
            "last_selected_language": self.last_selected_language,
            "last_selected_mode": self.last_selected_mode,
        }


def load_ui_preferences(config: DashboardConfig) -> UIPreferences:
    """Read UI preferences without creating or modifying files."""
    parser = ConfigParser()
    try:
        parser.read(config.ui_preferences_path, encoding="utf-8")
    except OSError:
        return UIPreferences()
    section = parser["ui"] if parser.has_section("ui") else {}
    return UIPreferences(
        language=_normalize_language_value(section.get("language"), allow_auto=True),
        start_mode=_normalize_mode(section.get("start_mode")),
        last_selected_language=_normalize_language_value(
            section.get("last_selected_language"),
            allow_auto=False,
        ),
        last_selected_mode=_normalize_mode(section.get("last_selected_mode")),
    )


def save_ui_preferences(config: DashboardConfig, payload: dict[str, Any]) -> UIPreferences:
    """Persist a whitelisted UI preference payload to the Bridge config file."""
    unknown_fields = sorted(set(payload) - ALLOWED_POST_FIELDS)
    if unknown_fields:
        raise ValueError(f"unsupported_ui_preference_field:{','.join(unknown_fields)}")
    warnings = config.validate_ui_preferences_path()
    if warnings:
        raise ValueError(f"invalid_ui_preferences_path:{','.join(warnings)}")

    current = load_ui_preferences(config).to_dict()
    for key, value in payload.items():
        if key == "language":
            current[key] = _normalize_language_value(value, allow_auto=True, strict=True)
            if current[key] != "auto" and "last_selected_language" not in payload:
                current["last_selected_language"] = current[key]
        elif key == "last_selected_language":
            current[key] = _normalize_language_value(value, allow_auto=False, strict=True)
        elif key == "start_mode":
            current[key] = _normalize_mode(value, strict=True)
            if "last_selected_mode" not in payload:
                current["last_selected_mode"] = current[key]
        elif key == "last_selected_mode":
            current[key] = _normalize_mode(value, strict=True)

    preferences = UIPreferences(**current)
    parser = ConfigParser()
    parser["ui"] = preferences.to_dict()
    target = config.ui_preferences_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        parser.write(handle)
    return preferences


def resolve_ui_language(
    config: DashboardConfig,
    *,
    query_lang: str | None,
    accept_language: str | None,
) -> tuple[str, str]:
    """Resolve language from URL, saved preference, browser header, then Italian fallback."""
    explicit = _match_supported_locale(query_lang)
    if explicit is not None:
        return explicit, "url"

    preferences = load_ui_preferences(config)
    if preferences.language != "auto":
        return preferences.language, "preference"

    detected = detect_accept_language(accept_language)
    if detected is not None:
        return detected, "accept-language"
    return DEFAULT_LAST_SELECTED_LANGUAGE, "fallback"


def detect_accept_language(value: str | None) -> str | None:
    """Return the first supported language from an Accept-Language header."""
    if not value:
        return None
    for raw_part in value.split(","):
        language = raw_part.split(";", 1)[0].strip()
        matched = _match_supported_locale(language)
        if matched is not None:
            return matched
    return None


def _normalize_language_value(
    value: object,
    *,
    allow_auto: bool,
    strict: bool = False,
) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    if allow_auto and text == "auto":
        return "auto"
    matched = _match_supported_locale(text)
    if matched is not None:
        return matched
    if strict:
        allowed = ",".join(SUPPORTED_LANGUAGE_VALUES if allow_auto else SUPPORTED_LOCALES)
        raise ValueError(f"invalid_language:{value};allowed:{allowed}")
    return DEFAULT_LANGUAGE if allow_auto else DEFAULT_LAST_SELECTED_LANGUAGE


def _normalize_mode(value: object, *, strict: bool = False) -> str:
    text = str(value or "").strip().lower()
    if text in SUPPORTED_MODES:
        return text
    if strict:
        raise ValueError(f"invalid_start_mode:{value};allowed:{','.join(SUPPORTED_MODES)}")
    return DEFAULT_START_MODE


def _match_supported_locale(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().lower().replace("_", "-")
    if not text:
        return None
    language = text.split("-", 1)[0]
    return language if language in SUPPORTED_LOCALES else None

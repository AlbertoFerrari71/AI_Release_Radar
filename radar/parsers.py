"""Offline fixture parsers for controlled release-radar inputs."""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Any

from radar.hash_utils import content_hash_for_item_fields, normalize_text, stable_item_id
from radar.models import Item


_REQUIRED_FIXTURE_FIELDS = (
    "natural_key",
    "category",
    "severity",
    "title",
    "published_at",
    "url",
    "evidence",
    "first_seen",
    "confidence",
)


def _item_sort_key(item: Item) -> tuple[str, str, str]:
    return (item.published_at, item.title, item.item_id)


def _sorted_items(items: list[Item]) -> list[Item]:
    return sorted(items, key=_item_sort_key)


def _require_non_empty_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} is required and must be a string.")
    normalized = normalize_text(value)
    if not normalized:
        raise ValueError(f"{field_name} is required and must not be empty.")
    return normalized


def _require_fixture_str(raw_item: dict[str, Any], field_name: str, context: str) -> str:
    if field_name not in raw_item:
        raise ValueError(f"{context}.{field_name} is required.")
    return _require_non_empty_str(raw_item[field_name], f"{context}.{field_name}")


def _require_confidence(raw_item: dict[str, Any], context: str) -> float:
    field_name = f"{context}.confidence"
    if "confidence" not in raw_item:
        raise ValueError(f"{field_name} is required.")

    value = raw_item["confidence"]
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number between 0 and 1.")
    if isinstance(value, str):
        text = normalize_text(value)
        if not text:
            raise ValueError(f"{field_name} must not be empty.")
        try:
            confidence = float(text)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a number between 0 and 1.") from exc
    elif isinstance(value, (int, float)):
        confidence = float(value)
    else:
        raise ValueError(f"{field_name} must be a number between 0 and 1.")

    if confidence < 0.0 or confidence > 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1.")
    return confidence


def _item_from_fixture_mapping(
    *,
    source_id: str,
    provider: str,
    raw_item: dict[str, Any],
    context: str,
) -> Item:
    normalized_source_id = _require_non_empty_str(source_id, "source_id")
    normalized_provider = _require_non_empty_str(provider, "provider")

    for field_name in _REQUIRED_FIXTURE_FIELDS:
        if field_name != "confidence":
            _require_fixture_str(raw_item, field_name, context)
    confidence = _require_confidence(raw_item, context)

    natural_key = _require_fixture_str(raw_item, "natural_key", context)
    category = _require_fixture_str(raw_item, "category", context)
    severity = _require_fixture_str(raw_item, "severity", context)
    title = _require_fixture_str(raw_item, "title", context)
    published_at = _require_fixture_str(raw_item, "published_at", context)
    url = _require_fixture_str(raw_item, "url", context)
    evidence = _require_fixture_str(raw_item, "evidence", context)
    first_seen = _require_fixture_str(raw_item, "first_seen", context)

    content_hash = content_hash_for_item_fields(
        source_id=normalized_source_id,
        provider=normalized_provider,
        category=category,
        severity=severity,
        title=title,
        published_at=published_at,
        url=url,
        evidence=evidence,
    )

    return Item(
        item_id=stable_item_id(normalized_source_id, natural_key),
        source_id=normalized_source_id,
        provider=normalized_provider,
        category=category,
        severity=severity,
        title=title,
        published_at=published_at,
        url=url,
        evidence=evidence,
        content_hash=content_hash,
        first_seen=first_seen,
        confidence=confidence,
    )


def parse_json_items_fixture(
    source_id: str,
    provider: str,
    fixture_data: object,
) -> list[Item]:
    """Parse a controlled JSON fixture mapping into deterministic Items."""
    if not isinstance(fixture_data, dict):
        raise ValueError("JSON fixture must be a dict with an items list.")
    raw_items = fixture_data.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("JSON fixture items must be a list.")

    items: list[Item] = []
    for index, raw_item in enumerate(raw_items):
        context = f"items[{index}]"
        if not isinstance(raw_item, dict):
            raise ValueError(f"{context} must be a dict.")
        items.append(
            _item_from_fixture_mapping(
                source_id=source_id,
                provider=provider,
                raw_item=raw_item,
                context=context,
            )
        )
    return _sorted_items(items)


class _SimpleReleaseHTMLParser(HTMLParser):
    """Parser for the 0040 controlled article fixture pattern only."""

    def __init__(self, source_id: str, provider: str) -> None:
        super().__init__(convert_charrefs=True)
        self._source_id = source_id
        self._provider = provider
        self._current_item: dict[str, Any] | None = None
        self._current_field: str | None = None
        self._text_chunks: list[str] = []
        self.items: list[Item] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value for name, value in attrs}
        if tag == "article":
            if self._current_item is not None:
                raise ValueError("HTML fixture has nested article blocks.")
            self._current_item = {
                "natural_key": attributes.get("data-release-id"),
                "first_seen": attributes.get("data-first-seen"),
                "confidence": attributes.get("data-confidence"),
            }
            return

        if self._current_item is None:
            return

        if tag == "h2":
            self._begin_text_field("title")
        elif tag == "time":
            if attributes.get("datetime") is not None:
                self._current_item["published_at"] = attributes["datetime"]
            self._begin_text_field("published_at_text")
        elif tag == "p":
            self._current_item["category"] = attributes.get("data-category")
            self._current_item["severity"] = attributes.get("data-severity")
            self._begin_text_field("evidence")
        elif tag == "a" and "url" not in self._current_item:
            self._current_item["url"] = attributes.get("href")

    def handle_data(self, data: str) -> None:
        if self._current_field is not None:
            self._text_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current_item is None:
            return

        if tag == "h2" and self._current_field == "title":
            self._end_text_field("title")
        elif tag == "time" and self._current_field == "published_at_text":
            text = normalize_text("".join(self._text_chunks))
            if "published_at" not in self._current_item and text:
                self._current_item["published_at"] = text
            self._clear_text_field()
        elif tag == "p" and self._current_field == "evidence":
            self._end_text_field("evidence")
        elif tag == "article":
            context = f"html article {len(self.items)}"
            self.items.append(
                _item_from_fixture_mapping(
                    source_id=self._source_id,
                    provider=self._provider,
                    raw_item=self._current_item,
                    context=context,
                )
            )
            self._current_item = None
            self._clear_text_field()

    def _begin_text_field(self, field_name: str) -> None:
        self._current_field = field_name
        self._text_chunks = []

    def _end_text_field(self, field_name: str) -> None:
        if self._current_item is None:
            return
        self._current_item[field_name] = normalize_text("".join(self._text_chunks))
        self._clear_text_field()

    def _clear_text_field(self) -> None:
        self._current_field = None
        self._text_chunks = []


def parse_simple_html_release_fixture(
    source_id: str,
    provider: str,
    html_text: str,
) -> list[Item]:
    """Parse the controlled 0040 HTML fixture pattern.

    This is deliberately not a real-world HTML parser. It only accepts the
    artificial article structure used by the offline fixture tests.
    """
    if not isinstance(html_text, str):
        raise ValueError("html_text must be a string.")
    parser = _SimpleReleaseHTMLParser(source_id, provider)
    parser.feed(html_text)
    parser.close()
    if parser._current_item is not None:
        raise ValueError("HTML fixture ended before closing an article block.")
    return _sorted_items(parser.items)


def parse_simple_text_release_fixture(
    source_id: str,
    provider: str,
    text: str,
) -> list[Item]:
    """Parse a controlled key/value text fixture into deterministic Items."""
    if not isinstance(text, str):
        raise ValueError("text must be a string.")

    raw_items: list[dict[str, str]] = []
    current_item: dict[str, str] | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped == "--- item ---":
            if current_item is not None:
                raw_items.append(current_item)
            current_item = {}
            continue
        if not stripped:
            continue
        if current_item is None:
            raise ValueError("Text fixture must start with '--- item ---'.")
        if ":" not in line:
            raise ValueError(f"Text fixture line {line_number} must be key: value.")
        key, value = line.split(":", 1)
        normalized_key = key.strip()
        if not normalized_key:
            raise ValueError(f"Text fixture line {line_number} has an empty key.")
        if normalized_key in current_item:
            raise ValueError(f"Text fixture line {line_number} duplicates {normalized_key}.")
        current_item[normalized_key] = value.strip()

    if current_item is not None:
        raw_items.append(current_item)

    items: list[Item] = []
    for index, raw_item in enumerate(raw_items):
        items.append(
            _item_from_fixture_mapping(
                source_id=source_id,
                provider=provider,
                raw_item=raw_item,
                context=f"text item {index}",
            )
        )
    return _sorted_items(items)

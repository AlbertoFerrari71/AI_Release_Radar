"""Offline fixture parsers for controlled release-radar inputs."""

from __future__ import annotations

from html.parser import HTMLParser
import re
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
_GITHUB_RELEASE_BODY_SUMMARY_MAX_CHARS = 500
_CODEX_CHANGELOG_MAX_CHARS = 20000
_CODEX_CHANGELOG_VERSION_RE = re.compile(
    r"\b[vV]?(?P<version>\d+\.\d+(?:\.\d+)?(?:[-.][A-Za-z0-9]+)?)\b"
)
_CODEX_CHANGELOG_DATE_RE = re.compile(r"\b(?P<date>\d{4}-\d{2}-\d{2})\b")


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


def parse_github_releases_api_fixture(
    source_id: str,
    provider: str,
    fixture_data: object,
    *,
    first_seen: str = "2026-06-10",
) -> list[Item]:
    """Parse a controlled offline fixture shaped like GitHub Releases API JSON."""
    normalized_source_id = _require_non_empty_str(source_id, "source_id")
    normalized_provider = _require_non_empty_str(provider, "provider")
    normalized_first_seen = _require_non_empty_str(first_seen, "first_seen")
    raw_releases = _github_releases_list(fixture_data)

    selected: dict[str, tuple[Item, tuple[str, str, str]]] = {}
    for index, raw_release in enumerate(raw_releases):
        context = f"releases[{index}]"
        if not isinstance(raw_release, dict):
            raise ValueError(f"{context} must be a dict.")
        item, rank = _github_release_item(
            source_id=normalized_source_id,
            provider=normalized_provider,
            first_seen=normalized_first_seen,
            raw_release=raw_release,
            context=context,
        )
        existing = selected.get(item.item_id)
        if existing is None or rank > existing[1]:
            selected[item.item_id] = (item, rank)

    return _sorted_items([item for item, _rank in selected.values()])


def _github_releases_list(fixture_data: object) -> list[object]:
    if isinstance(fixture_data, list):
        return list(fixture_data)
    if isinstance(fixture_data, dict):
        releases = fixture_data.get("releases")
        if isinstance(releases, list):
            return list(releases)
    raise ValueError("GitHub releases fixture must be a list or a dict with releases list.")


def _github_release_item(
    *,
    source_id: str,
    provider: str,
    first_seen: str,
    raw_release: dict[str, Any],
    context: str,
) -> tuple[Item, tuple[str, str, str]]:
    release_id = _optional_scalar_text(raw_release.get("id"), f"{context}.id")
    tag_name = _optional_str_field(raw_release, "tag_name", context)
    natural_key_value = release_id or tag_name
    if natural_key_value is None:
        raise ValueError(f"{context}.id or {context}.tag_name is required.")
    natural_key = f"github_release:{natural_key_value}"

    name = _optional_str_field(raw_release, "name", context)
    title = name or tag_name or f"GitHub release {natural_key_value}"
    html_url = _optional_str_field(raw_release, "html_url", context)
    api_url = _optional_str_field(raw_release, "url", context)
    url = html_url or api_url or ""
    published_at = _github_release_primary_timestamp(raw_release, context)
    updated_at = _optional_timestamp(raw_release.get("updated_at"), f"{context}.updated_at")
    draft = _optional_bool_field(raw_release, "draft", context)
    prerelease = _optional_bool_field(raw_release, "prerelease", context)
    body_summary = _github_release_body_summary(raw_release.get("body"), context)
    category = "codex_cli"
    severity = "info" if not draft else "low"
    evidence = _github_release_evidence(
        release_id=release_id,
        tag_name=tag_name,
        draft=draft,
        prerelease=prerelease,
        updated_at=updated_at,
        api_url=api_url,
        body_summary=body_summary,
    )
    content_hash = content_hash_for_item_fields(
        source_id=source_id,
        provider=provider,
        category=category,
        severity=severity,
        title=title,
        published_at=published_at,
        url=url,
        evidence=evidence,
    )
    item = Item(
        item_id=stable_item_id(source_id, natural_key),
        source_id=source_id,
        provider=provider,
        category=category,
        severity=severity,
        title=title,
        published_at=published_at,
        url=url,
        evidence=evidence,
        content_hash=content_hash,
        first_seen=first_seen,
        confidence=0.9 if not draft else 0.7,
    )
    rank = (updated_at or published_at, title, content_hash)
    return item, rank


def _optional_scalar_text(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a string, integer, or null.")
    if not isinstance(value, (str, int)):
        raise ValueError(f"{field_name} must be a string, integer, or null.")
    text = normalize_text(str(value))
    return text or None


def _optional_str_field(
    raw_release: dict[str, Any],
    field_name: str,
    context: str,
) -> str | None:
    value = raw_release.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{context}.{field_name} must be a string or null.")
    normalized = normalize_text(value)
    return normalized or None


def _optional_bool_field(
    raw_release: dict[str, Any],
    field_name: str,
    context: str,
) -> bool:
    value = raw_release.get(field_name, False)
    if not isinstance(value, bool):
        raise ValueError(f"{context}.{field_name} must be a boolean when provided.")
    return value


def _github_release_primary_timestamp(
    raw_release: dict[str, Any],
    context: str,
) -> str:
    published_at = _optional_timestamp(raw_release.get("published_at"), f"{context}.published_at")
    if published_at is not None:
        return published_at
    created_at = _optional_timestamp(raw_release.get("created_at"), f"{context}.created_at")
    if created_at is not None:
        return created_at
    updated_at = _optional_timestamp(raw_release.get("updated_at"), f"{context}.updated_at")
    if updated_at is not None:
        return updated_at
    raise ValueError(f"{context}.published_at, created_at, or updated_at is required.")


def _optional_timestamp(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO timestamp string or null.")
    timestamp = normalize_text(value)
    if not timestamp:
        return None
    try:
        from datetime import datetime

        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO timestamp string.") from exc
    return timestamp


def _github_release_body_summary(value: object, context: str) -> str:
    if value is None:
        return "No release body provided."
    if not isinstance(value, str):
        raise ValueError(f"{context}.body must be a string or null.")
    summary = normalize_text(value)
    if not summary:
        return "No release body provided."
    if len(summary) <= _GITHUB_RELEASE_BODY_SUMMARY_MAX_CHARS:
        return summary
    return summary[: _GITHUB_RELEASE_BODY_SUMMARY_MAX_CHARS - 3] + "..."


def _github_release_evidence(
    *,
    release_id: str | None,
    tag_name: str | None,
    draft: bool,
    prerelease: bool,
    updated_at: str | None,
    api_url: str | None,
    body_summary: str,
) -> str:
    metadata = [
        f"github_release_id={release_id or 'missing'}",
        f"tag_name={tag_name or 'missing'}",
        f"draft={str(draft).lower()}",
        f"prerelease={str(prerelease).lower()}",
        f"updated_at={updated_at or 'missing'}",
        f"api_url={api_url or 'missing'}",
    ]
    return "GitHub Releases API metadata: " + "; ".join(metadata) + f". Summary: {body_summary}"


def parse_codex_changelog_fixture(
    source_id: str,
    provider: str,
    content: str | bytes,
    *,
    first_seen: str = "2026-06-10",
    source_url: str = "https://developers.openai.com/codex/changelog",
    encoding: str = "utf-8",
    max_chars: int = _CODEX_CHANGELOG_MAX_CHARS,
) -> list[Item]:
    """Parse a controlled Codex changelog markdown/text fixture.

    This parser is intentionally conservative: it recognizes version headings,
    optional YYYY-MM-DD dates, section headings, and bullet lines only.
    """
    normalized_source_id = _require_non_empty_str(source_id, "source_id")
    normalized_provider = _require_non_empty_str(provider, "provider")
    normalized_first_seen = _require_non_empty_str(first_seen, "first_seen")
    normalized_source_url = _require_non_empty_str(source_url, "source_url")
    text = _decode_codex_changelog_content(content, encoding)
    if not text.strip():
        return []
    if not isinstance(max_chars, int) or isinstance(max_chars, bool) or max_chars < 1:
        raise ValueError("max_chars must be a positive integer.")
    if len(text) > max_chars:
        raise ValueError("Codex changelog content is too long.")

    entries = _codex_changelog_entries(text)
    items: list[Item] = []
    for entry in entries:
        items.append(
            _codex_changelog_item(
                source_id=normalized_source_id,
                provider=normalized_provider,
                first_seen=normalized_first_seen,
                source_url=normalized_source_url,
                entry=entry,
            )
        )
    return _sorted_items(items)


def _decode_codex_changelog_content(content: str | bytes, encoding: str) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, bytes):
        try:
            return content.decode(encoding)
        except (LookupError, UnicodeDecodeError) as exc:
            raise ValueError("Codex changelog content encoding is invalid.") from exc
    raise ValueError("content must be a string or bytes.")


def _codex_changelog_entries(text: str) -> list[dict[str, Any]]:
    entries: dict[tuple[str, str], dict[str, Any]] = {}
    current_version: str | None = None
    current_date: str | None = None
    current_section = "general"

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            version, date = _parse_codex_version_heading(stripped, line_number)
            if version is not None:
                current_version = version
                current_date = date
                current_section = "general"
                continue
            if current_version is not None and stripped.startswith("###"):
                current_section = _codex_section_name(stripped)
                continue
            continue
        bullet = _codex_bullet_text(stripped)
        if bullet is not None and current_version is not None:
            key = (current_version, _codex_section_name(current_section))
            entry = entries.setdefault(
                key,
                {
                    "version": current_version,
                    "date": current_date,
                    "section": _codex_section_name(current_section),
                    "bullets": set(),
                },
            )
            if entry["date"] is None and current_date is not None:
                entry["date"] = current_date
            entry["bullets"].add(bullet)

    return [
        entry
        for entry in sorted(
            entries.values(),
            key=lambda candidate: (
                candidate["date"] or "undated",
                candidate["version"],
                candidate["section"],
            ),
        )
        if entry["bullets"]
    ]


def _parse_codex_version_heading(
    stripped_line: str,
    line_number: int,
) -> tuple[str | None, str | None]:
    heading_text = stripped_line.lstrip("#").strip()
    version_match = _CODEX_CHANGELOG_VERSION_RE.search(heading_text)
    if version_match is None:
        return None, None
    date_match = _CODEX_CHANGELOG_DATE_RE.search(heading_text)
    date = None
    if date_match is not None:
        date = date_match.group("date")
        _validate_codex_changelog_date(date, line_number)
    return version_match.group("version"), date


def _validate_codex_changelog_date(date: str, line_number: int) -> None:
    try:
        from datetime import datetime

        datetime.strptime(date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"Codex changelog heading line {line_number} has an invalid date."
        ) from exc


def _codex_section_name(raw_section: str) -> str:
    section = raw_section.lstrip("#").strip()
    return normalize_text(section) or "general"


def _codex_bullet_text(stripped_line: str) -> str | None:
    if stripped_line.startswith("- ") or stripped_line.startswith("* "):
        return normalize_text(stripped_line[2:])
    return None


def _codex_changelog_item(
    *,
    source_id: str,
    provider: str,
    first_seen: str,
    source_url: str,
    entry: dict[str, Any],
) -> Item:
    version = _require_non_empty_str(entry["version"], "entry.version")
    section = _require_non_empty_str(entry["section"], "entry.section")
    published_at = (
        f"{entry['date']}T00:00:00Z" if entry.get("date") is not None else "undated"
    )
    bullets = sorted(entry["bullets"])
    summary = " ".join(bullets)
    natural_key = f"codex_changelog:{version}:{section.lower()}"
    category = _codex_category_from_section(section)
    severity = "info"
    title = f"Codex {version} - {section}"
    url = normalized_url = f"{source_url}#{_codex_anchor(version, section)}"
    evidence = (
        f"Codex changelog version={version}; section={section}; "
        f"date={entry.get('date') or 'missing'}. Summary: {summary}"
    )
    content_hash = content_hash_for_item_fields(
        source_id=source_id,
        provider=provider,
        category=category,
        severity=severity,
        title=title,
        published_at=published_at,
        url=normalized_url,
        evidence=evidence,
    )
    return Item(
        item_id=stable_item_id(source_id, natural_key),
        source_id=source_id,
        provider=provider,
        category=category,
        severity=severity,
        title=title,
        published_at=published_at,
        url=url,
        evidence=evidence,
        content_hash=content_hash,
        first_seen=first_seen,
        confidence=0.82 if published_at == "undated" else 0.88,
    )


def _codex_category_from_section(section: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", section.lower()).strip("_")
    if not token:
        return "codex_changelog"
    if token == "agents_md":
        return "codex_agents_md"
    if token.startswith("codex_"):
        return token
    return f"codex_{token}"


def _codex_anchor(version: str, section: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "-", f"{version}-{section}".lower()).strip("-")
    return token or "codex-changelog"


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

"""Build deterministic source snapshots from already parsed Items."""

from __future__ import annotations

from radar.hash_utils import normalize_text
from radar.models import SCHEMA_VERSION, Item, SourceSnapshot


def _item_sort_key(item: Item) -> tuple[str, str, str]:
    return (item.published_at, item.title, item.item_id)


def _require_non_empty_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    normalized = normalize_text(value)
    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")
    return normalized


def build_source_snapshot_from_items(
    source_id: str,
    provider: str,
    fetched_at: str,
    fetch_status: str,
    http_status: int | None,
    items: list[Item],
    page_hash: str | None = None,
) -> SourceSnapshot:
    """Build a SourceSnapshot without fetching or mutating item content."""
    normalized_source_id = _require_non_empty_str(source_id, "source_id")
    normalized_provider = _require_non_empty_str(provider, "provider")
    normalized_fetched_at = _require_non_empty_str(fetched_at, "fetched_at")
    normalized_fetch_status = _require_non_empty_str(fetch_status, "fetch_status")

    if not isinstance(items, list):
        raise ValueError("items must be a list of Item.")

    sorted_items: list[Item] = []
    for index, item in enumerate(items):
        if not isinstance(item, Item):
            raise ValueError(f"items[{index}] must be an Item.")
        if item.source_id != normalized_source_id:
            raise ValueError(f"items[{index}].source_id must match source_id.")
        if item.provider != normalized_provider:
            raise ValueError(f"items[{index}].provider must match provider.")
        sorted_items.append(item)

    return SourceSnapshot(
        schema_version=SCHEMA_VERSION,
        source_id=normalized_source_id,
        provider=normalized_provider,
        fetched_at=normalized_fetched_at,
        fetch_status=normalized_fetch_status,
        http_status=http_status,
        items=sorted(sorted_items, key=_item_sort_key),
        page_hash=page_hash,
    )

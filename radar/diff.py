"""Snapshot diffing logic."""

from __future__ import annotations

from radar.models import DiffResult, SourceSnapshot


def diff_snapshots(
    previous: SourceSnapshot | None,
    current: SourceSnapshot,
) -> DiffResult:
    """Return an item-level deterministic diff for two snapshots."""
    if not isinstance(current, SourceSnapshot):
        raise ValueError("current must be a SourceSnapshot.")
    if previous is not None and not isinstance(previous, SourceSnapshot):
        raise ValueError("previous must be a SourceSnapshot or None.")

    current_by_id = {item.item_id: item for item in current.items}

    if previous is None:
        return DiffResult(
            schema_version=current.schema_version,
            source_id=current.source_id,
            new_items=sorted(current_by_id),
            changed_items=[],
            removed_items=[],
            unchanged_count=0,
        )

    previous_by_id = {item.item_id: item for item in previous.items}

    new_items = sorted(set(current_by_id) - set(previous_by_id))
    removed_items = sorted(set(previous_by_id) - set(current_by_id))
    changed_items: list[str] = []
    unchanged_count = 0

    for item_id in sorted(set(current_by_id) & set(previous_by_id)):
        if current_by_id[item_id].content_hash != previous_by_id[item_id].content_hash:
            changed_items.append(item_id)
        else:
            unchanged_count += 1

    return DiffResult(
        schema_version=current.schema_version,
        source_id=current.source_id,
        new_items=new_items,
        changed_items=changed_items,
        removed_items=removed_items,
        unchanged_count=unchanged_count,
    )

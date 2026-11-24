"""Scheduling conflict detection (plain logic, no AI needed)."""
from typing import Iterable

from .models import Event


def find_conflicts(events: Iterable[Event]) -> list[tuple[Event, Event]]:
    """Return pairs of events whose time ranges overlap.

    Events that merely touch (one ends exactly when the next starts)
    are NOT conflicts. Runs in O(n log n + k) where k is the number of
    overlapping pairs, because events are sorted by start time and the
    inner loop stops at the first non-overlapping event.
    """
    ordered = sorted(events, key=lambda e: e.start)
    conflicts: list[tuple[Event, Event]] = []
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if b.start >= a.end:
                break
            conflicts.append((a, b))
    return conflicts

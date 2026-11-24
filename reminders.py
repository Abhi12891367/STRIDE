"""Decide which meeting reminders are due right now."""
from datetime import datetime
from typing import Iterable

from .dedupe import ReminderTracker
from .models import Event


def due_reminders(
    events: Iterable[Event],
    now: datetime,
    tracker: ReminderTracker,
    lead_minutes: int = 15,
) -> list[Event]:
    """Events starting within `lead_minutes` that have not been reminded yet."""
    due = []
    for event in events:
        minutes_until = (event.start - now).total_seconds() / 60
        if 0 < minutes_until <= lead_minutes and not tracker.already_sent(
            event.id, lead_minutes
        ):
            due.append(event)
    return sorted(due, key=lambda e: e.start)

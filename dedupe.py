"""Duplicate prevention for reminders.

The scheduler checks for upcoming meetings every 5 minutes, so without
this a single meeting could trigger several identical reminders. We record
each (event, lead-time) pair once and persist it to disk so restarts
do not cause repeats either.
"""
import json
from pathlib import Path
from typing import Optional


class ReminderTracker:
    def __init__(self, path: Optional[str] = None):
        self._path = Path(path) if path else None
        self._sent: set[str] = set()
        if self._path and self._path.exists():
            try:
                self._sent = set(json.loads(self._path.read_text()))
            except (json.JSONDecodeError, OSError):
                self._sent = set()

    @staticmethod
    def _key(event_id: str, lead_minutes: int) -> str:
        return f"{event_id}:{lead_minutes}"

    def already_sent(self, event_id: str, lead_minutes: int) -> bool:
        return self._key(event_id, lead_minutes) in self._sent

    def mark_sent(self, event_id: str, lead_minutes: int) -> None:
        self._sent.add(self._key(event_id, lead_minutes))
        if self._path:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(sorted(self._sent)))

from datetime import datetime, timedelta

from stride.dedupe import ReminderTracker
from stride.models import Event
from stride.reminders import due_reminders

NOW = datetime(2026, 11, 24, 9, 0)


def event(id, minutes_from_now):
    start = NOW + timedelta(minutes=minutes_from_now)
    return Event(id, id, start, start + timedelta(hours=1))


def test_reminder_sent_only_once():
    tracker = ReminderTracker()
    e = event("x", 10)
    assert due_reminders([e], NOW, tracker, 15) == [e]
    tracker.mark_sent("x", 15)
    # the next 5-minute check must not fire again
    assert due_reminders([e], NOW + timedelta(minutes=5), tracker, 15) == []


def test_only_upcoming_events_within_window():
    tracker = ReminderTracker()
    events = [event("past", -5), event("soon", 10), event("later", 60)]
    assert [e.id for e in due_reminders(events, NOW, tracker, 15)] == ["soon"]


def test_persists_across_restarts(tmp_path):
    path = str(tmp_path / "sent.json")
    ReminderTracker(path).mark_sent("x", 15)
    assert ReminderTracker(path).already_sent("x", 15)
    assert not ReminderTracker(path).already_sent("y", 15)

"""Calendar / email / deadline providers.

These demo providers generate sample data relative to "now" so Stride runs
end-to-end with zero credentials. To go live, implement the same methods
with the Gmail and Google Calendar APIs (see the Roadmap in the README).
"""
from datetime import datetime, timedelta
from typing import Protocol

from ..models import Deadline, Email, Event


class CalendarProvider(Protocol):
    def get_events(self, now: datetime) -> list[Event]: ...


class MailProvider(Protocol):
    def get_emails(self, now: datetime) -> list[Email]: ...


class DeadlineProvider(Protocol):
    def get_deadlines(self, now: datetime) -> list[Deadline]: ...


class DemoCalendar:
    def get_events(self, now: datetime) -> list[Event]:
        day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        h = timedelta(hours=1)
        return [
            Event("e1", "Data Structures Lecture", day + timedelta(hours=9), day + timedelta(hours=10, minutes=30), "Room 204"),
            Event("e2", "Project Sync", day + timedelta(hours=10), day + timedelta(hours=11), "Discord VC"),  # overlaps e1
            Event("e3", "Lab Session", day + timedelta(hours=14), day + timedelta(hours=14) + 2 * h, "CS Lab"),
            Event("soon", "Study Group", now + timedelta(minutes=10), now + timedelta(minutes=70), "Library"),
            Event("e4", "Algorithms Quiz", day + timedelta(days=1, hours=11), day + timedelta(days=1, hours=12), "Hall B"),
        ]


class DemoMail:
    def get_emails(self, now: datetime) -> list[Email]:
        return [
            Email("m1", "Prof. Rao", "Assignment 3 clarification", "Please read the updated rubric...", now - timedelta(hours=3), needs_action=True),
            Email("m2", "Placement Cell", "Register for campus drive", "Registration closes Friday...", now - timedelta(hours=5), needs_action=True),
            Email("m3", "Newsletter", "Weekly campus digest", "This week on campus...", now - timedelta(hours=8)),
        ]


class DemoDeadlines:
    def get_deadlines(self, now: datetime) -> list[Deadline]:
        return [
            Deadline("d1", "Assignment 3", now + timedelta(days=1, hours=2), "Algorithms"),
            Deadline("d2", "Lab report", now + timedelta(days=2), "Operating Systems"),
            Deadline("d3", "Term paper draft", now + timedelta(days=9), "Ethics"),
        ]

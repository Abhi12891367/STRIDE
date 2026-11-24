from datetime import datetime, timedelta

from stride.briefing import evening_recap, morning_briefing
from stride.models import Deadline, Email, Event, Weather

NOW = datetime(2026, 11, 24, 7, 30)


def test_morning_briefing_contains_all_sections():
    events = [
        Event("a", "Lecture", NOW.replace(hour=9, minute=0), NOW.replace(hour=10, minute=30)),
        Event("b", "Sync", NOW.replace(hour=10, minute=0), NOW.replace(hour=11, minute=0)),
    ]
    emails = [Email("m", "Prof", "Reply needed", "...", NOW, needs_action=True)]
    deadlines = [Deadline("d", "Assignment", NOW + timedelta(days=1))]
    text = morning_briefing(NOW, events, emails, deadlines, Weather(24, 28, 20, 70))
    assert "Lecture" in text and "overlaps" in text
    assert "Assignment" in text
    assert "Reply needed" in text
    assert "umbrella" in text


def test_briefing_handles_missing_weather_and_empty_day():
    text = morning_briefing(NOW, [], [], [], None)
    assert "Weather unavailable" in text
    assert "Nothing scheduled" in text


def test_evening_recap_lists_tomorrow():
    tomorrow = NOW + timedelta(days=1)
    events = [Event("q", "Quiz", tomorrow.replace(hour=11, minute=0), tomorrow.replace(hour=12, minute=0))]
    assert "Quiz" in evening_recap(NOW, events, [], [])

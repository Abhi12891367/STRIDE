"""Builds the daily briefing and evening recap messages."""
from datetime import datetime, timedelta
from typing import Optional, Sequence

from .conflicts import find_conflicts
from .models import Deadline, Email, Event, Weather


def _t(dt: datetime) -> str:
    return dt.strftime("%I:%M %p").lstrip("0")


def _weather_line(w: Optional[Weather]) -> str:
    if w is None:
        return "Weather unavailable right now."
    tip = " Carry an umbrella." if w.rain_chance >= 50 else ""
    return (
        f"{w.temp_c:.0f}°C now (high {w.high_c:.0f}°, low {w.low_c:.0f}°), "
        f"{w.rain_chance}% chance of rain.{tip}"
    )


def _events_on(events: Sequence[Event], day) -> list[Event]:
    return sorted((e for e in events if e.start.date() == day), key=lambda e: e.start)


def _upcoming(deadlines: Sequence[Deadline], now: datetime, days: int) -> list[Deadline]:
    limit = now + timedelta(days=days)
    return sorted((d for d in deadlines if now <= d.due <= limit), key=lambda d: d.due)


def _conflict_lines(events: Sequence[Event]) -> list[str]:
    return [
        f"⚠️ **{a.title}** ({_t(a.start)}-{_t(a.end)}) overlaps **{b.title}** "
        f"({_t(b.start)}-{_t(b.end)})"
        for a, b in find_conflicts(events)
    ]


def morning_briefing(
    now: datetime,
    events: Sequence[Event],
    emails: Sequence[Email],
    deadlines: Sequence[Deadline],
    weather: Optional[Weather],
) -> str:
    today = _events_on(events, now.date())
    lines = [f"☀️ **Good morning! Your briefing for {now:%A, %d %B}**", ""]
    lines += [f"🌤️ **Weather:** {_weather_line(weather)}", ""]

    lines.append("📅 **Today's schedule**")
    lines += [f"• {_t(e.start)} - {e.title}" + (f" @ {e.location}" if e.location else "")
              for e in today] or ["• Nothing scheduled. Nice."]
    lines.append("")

    conflicts = _conflict_lines(today)
    if conflicts:
        lines += ["**Conflicts detected**", *conflicts, ""]

    due = _upcoming(deadlines, now, days=3)
    lines.append("📚 **Deadlines in the next 3 days**")
    lines += [f"• {d.title}" + (f" ({d.course})" if d.course else "")
              + f" - due {d.due:%a %d %b, %I:%M %p}" for d in due] or ["• None. You're clear."]
    lines.append("")

    action = [m for m in emails if m.needs_action]
    lines.append("📧 **Emails needing action**")
    lines += [f"• {m.sender}: {m.subject}" for m in action] or ["• Inbox looks calm."]
    return "\n".join(lines)


def evening_recap(
    now: datetime,
    events: Sequence[Event],
    emails: Sequence[Email],
    deadlines: Sequence[Deadline],
) -> str:
    tomorrow = (now + timedelta(days=1)).date()
    events_tomorrow = _events_on(events, tomorrow)
    lines = [f"🌙 **Evening recap - {now:%A, %d %B}**", ""]

    lines.append("📅 **Tomorrow**")
    lines += [f"• {_t(e.start)} - {e.title}" for e in events_tomorrow] or ["• Nothing scheduled."]
    lines.append("")

    conflicts = _conflict_lines(events_tomorrow)
    if conflicts:
        lines += ["**Conflicts tomorrow**", *conflicts, ""]

    due = _upcoming(deadlines, now, days=2)
    lines.append("⏰ **Due within 48 hours**")
    lines += [f"• {d.title} - {d.due:%a %d %b, %I:%M %p}" for d in due] or ["• Nothing urgent."]
    lines.append("")

    pending = [m for m in emails if m.needs_action]
    lines.append(f"📧 **Still need a reply:** {len(pending)}")
    return "\n".join(lines)


def reminder_message(event: Event, now: datetime) -> str:
    mins = max(1, round((event.start - now).total_seconds() / 60))
    where = f" @ {event.location}" if event.location else ""
    return f"🔔 **{event.title}** starts in {mins} min ({_t(event.start)}){where}"

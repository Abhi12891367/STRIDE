"""Configuration loaded from environment variables (see .env.example)."""
import os
from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


def _parse_time(value: str, tz: ZoneInfo) -> time:
    return datetime.strptime(value, "%H:%M").time().replace(tzinfo=tz)


@dataclass(frozen=True)
class Config:
    discord_token: str
    channel_id: int
    timezone: ZoneInfo
    latitude: float
    longitude: float
    briefing_time: time
    recap_time: time
    reminder_lead_minutes: int

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        tz = ZoneInfo(os.getenv("TIMEZONE", "Asia/Kolkata"))
        token = os.getenv("DISCORD_TOKEN")
        channel = os.getenv("DISCORD_CHANNEL_ID")
        if not token or not channel:
            raise RuntimeError(
                "DISCORD_TOKEN and DISCORD_CHANNEL_ID must be set. "
                "Copy .env.example to .env and fill them in."
            )
        return cls(
            discord_token=token,
            channel_id=int(channel),
            timezone=tz,
            latitude=float(os.getenv("LATITUDE", "12.9716")),
            longitude=float(os.getenv("LONGITUDE", "77.5946")),
            briefing_time=_parse_time(os.getenv("BRIEFING_TIME", "07:30"), tz),
            recap_time=_parse_time(os.getenv("RECAP_TIME", "20:00"), tz),
            reminder_lead_minutes=int(os.getenv("REMINDER_LEAD_MINUTES", "15")),
        )

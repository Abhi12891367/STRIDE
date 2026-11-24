"""Plain data types shared across Stride."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Event:
    id: str
    title: str
    start: datetime
    end: datetime
    location: str = ""


@dataclass(frozen=True)
class Email:
    id: str
    sender: str
    subject: str
    snippet: str
    received: datetime
    needs_action: bool = False


@dataclass(frozen=True)
class Deadline:
    id: str
    title: str
    due: datetime
    course: str = ""


@dataclass(frozen=True)
class Weather:
    temp_c: float
    high_c: float
    low_c: float
    rain_chance: int  # percent

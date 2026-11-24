"""Weather via Open-Meteo (free, no API key)."""
from typing import Optional

import requests

from ..models import Weather

URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(lat: float, lon: float) -> Optional[Weather]:
    try:
        resp = requests.get(
            URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 1,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return Weather(
            temp_c=data["current"]["temperature_2m"],
            high_c=data["daily"]["temperature_2m_max"][0],
            low_c=data["daily"]["temperature_2m_min"][0],
            rain_chance=int(data["daily"]["precipitation_probability_max"][0] or 0),
        )
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None  # the briefing degrades gracefully without weather

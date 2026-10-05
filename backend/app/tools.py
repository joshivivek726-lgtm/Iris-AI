"""Simple tools that give Iris real-world information"""

import logging
from datetime import datetime
from typing import Optional
import re
import requests
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

DEFAULT_CITY = "Wesley Chapel"

def get_current_time() -> str:
    now = datetime.now()
    return now.strftime("The current date is %A, %B %d, %Y, and the time is %I:%M %p.")

WEATHER_CODES = {
    0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "rain showers", 81: "rain showers", 82: "heavy rain showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail",
}

def get_weather(city: str) -> str:
    """Current weather for a city using Open-Meteo (no API key needed)."""
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        timeout=10,
    ).json()
    if not geo.get("results"):
        return f"I couldn't find a place called {city}."
    place = geo["results"][0]
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,wind_speed_10m,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
        },
        timeout=10,
    ).json()["current"]
    sky = WEATHER_CODES.get(weather["weather_code"], "unknown conditions")
    return (
        f"Current weather in {place['name']}: {sky}, "
        f"{weather['temperature_2m']}°F, wind {weather['wind_speed_10m']} mph."
    )

def web_search(query: str) -> str:
    """Latest news headlines via Google News RSS (no API key)."""
    topic = re.sub(
        r"(?i)\b(search for|look up|google|(the )?latest news( about| on)?|news about)\b",
        "",
        query,
    ).strip(" ?.!")
    resp = requests.get(
        "https://news.google.com/rss/search",
        params={"q": topic or query, "hl": "en-US", "gl": "US", "ceid": "US:en"},
        timeout=10,
    )
    resp.raise_for_status()
    items = ET.fromstring(resp.content).findall("./channel/item")[:4]
    if not items:
        return "No news results found."
    return "Latest news headlines:\n" + "\n".join(
        f"- {i.findtext('title')} ({i.findtext('pubDate')})" for i in items
    )

def run_tools(message: str) -> Optional[str]:
    """Return tool output if the message needs it, otherwise None."""
    text = message.lower()
    if any(w in text for w in ["what time", "what's the time", "current time", "what day", "today's date", "what date", "what is the date"]):
        logger.info("Tool used: time")
        return get_current_time()
    if "weather" in text or "temperature" in text:
        match = re.search(r"\bin ([a-zA-Z ]+?)(?:[?.!,]|$)", message)
        city = match.group(1).strip() if match else DEFAULT_CITY
        logger.info(f"Tool used: weather ({city})")
        try:
            return get_weather(city)
        except Exception as e:
            logger.error(f"Weather tool failed: {e}")
            return "The weather service is unavailable right now."
    if any(w in text for w in ["search for", "look up", "latest news", "news about", "who won", "google"]):
        logger.info("Tool used: web search")
        try:
            return web_search(message)
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return "The web search failed. Tell the user you could not look it up. Do not guess."
    return None

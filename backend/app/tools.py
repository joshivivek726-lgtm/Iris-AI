"""Simple tools that give Iris real-world information"""

import logging
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_search_cache = {}  # query -> (timestamp, result)
CACHE_SECONDS = 300

DEFAULT_CITY = "Wesley Chapel"

WEB_SEARCH_INTENT = re.compile(
    r"\b(?:"
    r"search(?:\s+for)?|look\s+up|google|find\s+online|"
    r"latest|newest|recent|recently|current|currently|now|future|update|updates|"
    r"what(?:'s| is) new|what happened|what(?:'s| has) happened|happening|"
    r"today|yesterday|tomorrow|this\s+(?:week|month|year)|"
    r"as\s+of|so\s+far|to\s+date|upcoming|scheduled|announced|"
    r"status\s+of|results\s+for|who\s+won|who\s+is\s+leading|"
    r"historical|history\s+of|previous|in\s+the\s+past|expected|"
    r"polls?|polling|elections?|midterms?|scores?|standings|since|"
    r"(?:19|20)\d{2}"
    r")\b",
    re.IGNORECASE,
)


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
    """Latest headlines via Google News RSS (no API key, not rate limited)."""
    topic = re.sub(
        r"(?i)\b(search for|look up|google|what are|what is|who are|who is|tell me about|show me|find|the latest|latest news|current news|news about|i want|total)\b",
        "",
        query,
    ).strip(" ?.!")
    search_query = topic or query
    search_query = re.sub(r"(?i)\bwhats\s+(?:the\s+)?score\b", "score", search_query)
    search_query = re.sub(r"(?i)\bindian\s+vs\b", "India vs", search_query)
    if (
        "score" in search_query.lower()
        and any(t in search_query.lower() for t in ("cricket", "west indies", "t20", "20-20", "20 20"))
    ):
        search_query = re.sub(r"(?i)\b20[- ]20\b", "T20", search_query)
        search_query = re.sub(r"(?i)\bmatch happened\b", "match", search_query)
        if "cricket" not in search_query.lower():
            search_query += " cricket"

    cached = _search_cache.get(search_query)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]

    try:
        resp = requests.get(
            "https://news.google.com/rss/search",
            params={"q": search_query + " when:7d", "hl": "en-US", "gl": "US", "ceid": "US:en"},
            timeout=10,
        )
        resp.raise_for_status()
        items = ET.fromstring(resp.content).findall("./channel/item")[:5]
    except Exception as e:
        logger.error("News search failed: %s", e)
        return "Web search failed. Please try again shortly."

    if not items:
        return f"No search results found for: {search_query}"

    output = "Web search results:\n" + "\n".join(
        f"- {i.findtext('title')} ({i.findtext('pubDate')})" for i in items
    )
    _search_cache[search_query] = (time.time(), output)
    return output


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
    if WEB_SEARCH_INTENT.search(message):
        logger.info("Tool used: web search")
        try:
            return web_search(message)
        except Exception as e:
         logger.error("Web search failed: %s", e)
         return "Web search failed. Please try again shortly."
        
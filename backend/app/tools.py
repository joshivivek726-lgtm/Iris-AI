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


FOLLOW_UP = re.compile(
    r"\b(?:then|regarding|i\s+asked|i\s+meant|as\s+i\s+said|that\s+match|that\s+game|same\s+match|scores?|results?|outcome|winner|i\s+want)\b",
    re.IGNORECASE,
)


def get_current_time() -> str:
    now = datetime.now()
    return now.strftime("The current date is %A, %B %d, %Y, and the time is %I:%M %p.")


WEATHER_CODES = {
    0: "clear sky",
    1: "mostly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "foggy",
    51: "light drizzle",
    53: "drizzle",
    55: "heavy drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    71: "light snow",
    73: "snow",
    75: "heavy snow",
    80: "rain showers",
    81: "rain showers",
    82: "heavy rain showers",
    95: "thunderstorm",
    96: "thunderstorm with hail",
    99: "thunderstorm with hail",
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
        r"(?i)\b(search for|look up|google|what are|what is|who are|who is|tell me about|show me|find|the latest|latest news|current news|news about|i want|total|whats|what's|then|regarding|i asked|i meant|as i said|for yesterday|held on|the result of)\b",
        "",
        query,
    )
    search_query = re.sub(r"\s+", " ", topic or query).strip(" ?.!")
    search_query = re.sub(r"(?i)\bindian\s+vs\b", "India vs", search_query)
    search_query = re.sub(r"(?i)\bman\s*city\b|\bmancity\b", "Manchester City", search_query)
    search_query = re.sub(r"(?i)\bman\s*(?:u|utd|united)\b", "Manchester United", search_query)
    search_query = re.sub(r"(?i)\bwest\s*indies\b", "West Indies", search_query)
    lowered = search_query.lower()
    if "score" in lowered and any(t in lowered for t in ("cricket", "west indies", "t20", "20-20", "20 20")):
        search_query = re.sub(r"(?i)\b20[- ]20\b", "T20", search_query)
        if "cricket" not in lowered:
            search_query += " cricket"

    cached = _search_cache.get(search_query)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]

    items = []
    errors = 0
    # Try the last 7 days first, then fall back to any date
    for q in (search_query + " when:7d", search_query):
        try:
            resp = requests.get(
                "https://news.google.com/rss/search",
                params={"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"},
                timeout=10,
            )
            resp.raise_for_status()
            items = ET.fromstring(resp.content).findall("./channel/item")[:6]
        except Exception as e:
            errors += 1
            logger.error("News search failed: %s", e)
            continue
        if items:
            break

    if not items:
        if errors == 2:
            return "Web search failed. Please try again shortly."
        return f"I could not find any recent news about: {search_query}."

    output = "Web search results:\n" + "\n".join(
        f"- {i.findtext('title')} ({i.findtext('pubDate')})" for i in items
    )
    _search_cache[search_query] = (time.time(), output)
    return output


QUESTION_START = re.compile(
    r"^\s*(?:is|are|was|were|did|does|do|has|have|had|will|can|could|who|whom|whose|what|whats|what's|when|where|which|why|how)\b",
    re.IGNORECASE,
)
NO_SEARCH = re.compile(
    r"\b(?:my\s+name|remember|who\s+am\s+i|your\s+name|who\s+are\s+you|thank|thanks|joke|poem|story|write\s+me|translate)\b",
    re.IGNORECASE,
)
MATH = re.compile(r"\d\s*(?:[-+*/x]|plus|minus|times|divided\s+by)\s*\d", re.IGNORECASE)


def needs_search(message: str, history: Optional[list] = None) -> bool:
    """Search for explicit requests, follow-ups, and any factual question."""
    if WEB_SEARCH_INTENT.search(message) or _is_short_follow_up(message, history):
        return True
    if NO_SEARCH.search(message) or MATH.search(message):
        return False
    if len(re.findall(r"[A-Za-z0-9]+", message)) < 3:
        return False
    return bool(QUESTION_START.search(message)) or message.strip().endswith("?")


def run_tools(message: str, history: Optional[list] = None) -> Optional[str]:
    """Return tool output if the message needs it, otherwise None."""
    text = message.lower()
    if any(
        w in text
        for w in [
            "what time",
            "what's the time",
            "current time",
            "what day",
            "today's date",
            "what date",
            "what is the date",
        ]
    ):
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
    if needs_search(message, history):
        logger.info("Tool used: web search")
        try:
            return web_search(_with_context(message, history))
        except Exception as e:
            logger.error("Web search failed: %s", e)
            return "Web search failed. Please try again shortly."
    return None


def _is_short_follow_up(message: str, history: Optional[list]) -> bool:
    return (
        bool(history) and len(message.split()) <= 10 and bool(FOLLOW_UP.search(message))
    )


def _with_context(message: str, history: Optional[list]) -> str:
    """For short follow-ups, prepend the user's last substantial question."""
    if not _is_short_follow_up(message, history):
        return message
    for m in reversed(history):
        if m.get("role") == "user" and len(m.get("content", "").split()) >= 6:
            return f"{m['content']} {message}"
    return message

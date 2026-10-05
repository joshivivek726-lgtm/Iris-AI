"""Simple tools that give Iris real-world information"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def get_current_time() -> str:
    now = datetime.now()
    return now.strftime("The current date is %A, %B %d, %Y, and the time is %I:%M %p.")


def run_tools(message: str) -> Optional[str]:
    """Return tool output if the message needs it, otherwise None."""
    text = message.lower()
    if any(w in text for w in ["what time", "what's the time", "current time", "what day", "today's date", "what date", "what is the date"]):
        logger.info("Tool used: time")
        return get_current_time()
    return None
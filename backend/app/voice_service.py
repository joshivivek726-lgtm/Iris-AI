"""Speech-to-text service using Whisper"""

import logging
import re
import whisper

logger = logging.getLogger(__name__)

_model = None


def get_model(name: str = "base"):
    """Load the Whisper model once and reuse it."""
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model: {name}")
        _model = whisper.load_model(name)
    return _model


def transcribe_file(path: str) -> str:
    """Transcribe an audio file to text."""
    result = get_model().transcribe(path, fp16=False)
    text = result["text"].strip()
    return re.sub(r"\b(Eris|Irish|Ayris)\b", "Iris", text)
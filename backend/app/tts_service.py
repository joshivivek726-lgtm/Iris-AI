"""Text-to-speech service using the macOS built-in `say` command"""

import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def speak(text: str, voice: Optional[str] = None) -> None:
    """Start speaking text aloud and return immediately."""
    text = text.strip()
    if not text:
        return
    cmd = ["say"]
    if voice:
        cmd += ["-v", voice]
    cmd += ["-f", "-"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    proc.stdin.write(text.encode("utf-8"))
    proc.stdin.close()
    logger.info(f"Speaking {len(text)} characters")
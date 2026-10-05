"""Text-to-speech service using the macOS built-in `say` command"""

import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def speak(text: str, voice: Optional[str] = None) -> None:
    """Speak text aloud on the machine running the server."""
    text = text.strip()
    if not text:
        return
    cmd = ["say"]
    if voice:
        cmd += ["-v", voice]
    cmd += ["-f", "-"]
    # Text goes in through stdin, so it can never be read as a command option
    result = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"say failed: {result.stderr.decode().strip()}")
    logger.info(f"Spoke {len(text)} characters")
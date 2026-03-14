import re
from datetime import datetime
from typing import AsyncGenerator

from .process_manager import ProcessManager

_STRUCTURED_RE = re.compile(
    r"^(\d{2}:\d{2}:\d{2}\.\d{3})\s+"
    r"(INFO|DEBUG|WARNING|ERROR|CRITICAL)\s+"
    r"(.*)",
)
_UVICORN_PREFIX_RE = re.compile(r"^[A-Z]+:\s+")
_LEVEL_RE = re.compile(
    r"\b(INFO|DEBUG|WARNING|ERROR|CRITICAL|WARN)\b", re.IGNORECASE
)

_LEVEL_CSS = {
    "ERROR": "error",
    "CRITICAL": "error",
    "WARNING": "warning",
    "WARN": "warning",
    "DEBUG": "debug",
}


def _parse_line(line: str) -> tuple[str, str, str]:
    """Return (timestamp, css_level, message)."""
    m = _STRUCTURED_RE.match(line)
    if m:
        ts, level_str, msg = m.group(1), m.group(2), m.group(3)
        return ts, _LEVEL_CSS.get(level_str, "info"), msg

    # fallback: legacy uvicorn format or bare lines
    lm = _LEVEL_RE.search(line)
    css = _LEVEL_CSS.get(lm.group(1).upper(), "info") if lm else "info"
    ts = datetime.now().strftime("%H:%M:%S")
    msg = _UVICORN_PREFIX_RE.sub("", line)
    return ts, css, msg


async def stream_log_events(
    process_manager: ProcessManager, volume_id: str, chapter_id: str, lesson_id: str
) -> AsyncGenerator[str, None]:
    async for line in process_manager.stream_logs(volume_id, chapter_id, lesson_id):
        ts, level, msg = _parse_line(line)
        safe_msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html = (
            f'<div class="log-entry log-{level}">'
            f'<span class="log-time">{ts}</span>'
            f'<span class="log-level">{level.upper()}</span>'
            f'<span class="log-msg">{safe_msg}</span>'
            f"</div>"
        )
        yield html

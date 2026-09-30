from __future__ import annotations

from typing import Any


def strip_cache_breakpoints(messages: list[dict[str, Any]]) -> None:
    """Remove CrewAI cache metadata unsupported by Groq's OpenAI-compatible API."""
    for message in messages:
        message.pop("cache_breakpoint", None)

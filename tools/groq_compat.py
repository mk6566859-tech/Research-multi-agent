from __future__ import annotations

from typing import Any


MAX_GROQ_PROMPT_BYTES = 5000
TRUNCATION_MARKER = "\n[Earlier context omitted to stay within Groq's request limit.]\n"


def prepare_groq_messages(messages: list[dict[str, Any]]) -> None:
    """Keep CrewAI messages within a conservative Groq request-token budget."""
    for message in messages:
        message.pop("cache_breakpoint", None)

    text_messages = [
        message
        for message in messages
        if isinstance(message.get("content"), str)
    ]
    unsupported_content = [
        message.get("content")
        for message in messages
        if message.get("content") is not None
        and not isinstance(message.get("content"), str)
    ]
    if unsupported_content:
        raise TypeError("Groq prompt budgeting only supports text message content.")

    prompt_size = sum(
        len(message["content"].encode("utf-8")) for message in text_messages
    )
    if prompt_size <= MAX_GROQ_PROMPT_BYTES:
        return

    marker = TRUNCATION_MARKER.encode("utf-8")
    candidates = sorted(
        text_messages,
        key=lambda message: (
            message.get("role") == "system",
            -len(message["content"].encode("utf-8")),
        ),
    )
    for message in candidates:
        if prompt_size <= MAX_GROQ_PROMPT_BYTES:
            break

        content = message["content"].encode("utf-8")
        excess = prompt_size - MAX_GROQ_PROMPT_BYTES
        keep_size = max(0, len(content) - excess - len(marker))
        if len(content) < len(marker):
            message["content"] = ""
        else:
            prefix_size = (keep_size + 1) // 2
            suffix_size = keep_size - prefix_size
            prefix = content[:prefix_size].decode("utf-8", errors="ignore")
            suffix = content[-suffix_size:].decode("utf-8", errors="ignore") if suffix_size else ""
            message["content"] = f"{prefix}{TRUNCATION_MARKER}{suffix}"
        prompt_size = sum(
            len(item["content"].encode("utf-8"))
            for item in text_messages
        )

    if prompt_size > MAX_GROQ_PROMPT_BYTES:
        raise ValueError("Unable to fit Groq prompt within the configured request budget.")

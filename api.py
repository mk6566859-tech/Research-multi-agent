"""
api.py - Centralized API, LLM, and Secrets Management for ResearchPilot AI.

Responsible for:
- Reading API secrets from Streamlit secrets (Streamlit Cloud) or environment variables.
- Initializing the centralized Groq LLM instance for CrewAI agents.
- Managing model selection (default: openai/gpt-oss-120b).
- Providing clear validation and error handling without exposing secrets.
"""

from __future__ import annotations

import os
from typing import Any

from crewai import LLM

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_MAX_COMPLETION_TOKENS = 1024


def get_secret(key: str, default: str | None = None) -> str | None:
    """
    Safely retrieve a secret from Streamlit secrets (st.secrets) or environment variables.
    Never exposes secrets in logs or exceptions.
    """
    # 1. Attempt retrieval from Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
            if val is not None and str(val).strip():
                return str(val).strip()
    except Exception:
        pass

    # 2. Attempt retrieval from environment variables
    env_val = os.environ.get(key)
    if env_val is not None and env_val.strip():
        return env_val.strip()

    return default


def get_groq_api_key() -> str:
    """Retrieve the Groq API key or raise a user-friendly error."""
    key = get_secret("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY is missing. Please set your GROQ_API_KEY in "
            ".streamlit/secrets.toml (locally) or in the Streamlit Cloud Secrets settings."
        )
    return key


def get_tavily_api_key() -> str:
    """Retrieve the Tavily API key or raise a user-friendly error."""
    key = get_secret("TAVILY_API_KEY")
    if not key:
        raise ValueError(
            "TAVILY_API_KEY is missing. Please set your TAVILY_API_KEY in "
            ".streamlit/secrets.toml (locally) or in the Streamlit Cloud Secrets settings."
        )
    return key


def get_groq_model() -> str:
    """Retrieve the configured Groq model name, defaulting to openai/gpt-oss-120b."""
    return get_secret("GROQ_MODEL", DEFAULT_GROQ_MODEL) or DEFAULT_GROQ_MODEL


def format_groq_model_identifier(model_name: str) -> str:
    """
    Ensure the model identifier is properly prefixed with 'groq/' for CrewAI's LiteLLM handler.
    Example: 'openai/gpt-oss-120b' -> 'groq/openai/gpt-oss-120b'
    Avoids double-prefixing if already starts with 'groq/'.
    """
    clean_name = model_name.strip()
    if clean_name.startswith("groq/"):
        return clean_name
    return f"groq/{clean_name}"


def get_crewai_llm(
    model_name: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = GROQ_MAX_COMPLETION_TOKENS,
) -> LLM:
    """
    Initialize and return a centralized CrewAI LLM instance configured for Groq.
    Requires litellm to be installed (included in requirements.txt).
    Agents reuse this single configuration without hardcoding credentials.
    """
    api_key = get_groq_api_key()

    # LiteLLM looks for GROQ_API_KEY in the environment
    os.environ["GROQ_API_KEY"] = api_key

    selected_model = model_name or get_groq_model()
    model_identifier = format_groq_model_identifier(selected_model)

    return LLM(
        model=model_identifier,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def validate_api_keys() -> tuple[bool, str]:
    """
    Check if required API credentials are present without exposing their values.
    Returns (is_valid, user_message).
    """
    missing = []
    if not get_secret("GROQ_API_KEY"):
        missing.append("GROQ_API_KEY")
    if not get_secret("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")

    if missing:
        return False, f"Missing required credentials: {', '.join(missing)}."
    return True, "API keys validated successfully."

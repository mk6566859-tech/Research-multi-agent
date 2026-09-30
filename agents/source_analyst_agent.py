"""
agents/source_analyst_agent.py - Agent 3: Source Analyst.

Responsibilities:
- Analyze the sources collected by the Web Researcher.
- Extract important claims, statistics, and empirical findings.
- Identify which sources support which claims.
- Detect and filter weak, duplicate, irrelevant, or low-credibility sources.
- Organize evidence systematically by research subtopic.
- Rigorously preserve Source IDs and URLs.
- Prepare structured evidence for the fact-checking stage.
- Never creates unsupported claims.
"""

from __future__ import annotations

from typing import Any
import yaml
from pathlib import Path

from crewai import Agent, LLM
from api import get_crewai_llm


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agents.yaml"


def _load_analyst_config() -> dict[str, Any]:
    """Load source analyst configuration from config/agents.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "source_analyst" in data:
                return data["source_analyst"]
    return {
        "role": "Senior Evidence & Source Analyst",
        "goal": "Analyze collected sources, extract verifiable claims, and structure evidence by subtopic.",
        "backstory": "A meticulous intelligence and source evaluation analyst."
    }


def create_source_analyst_agent(llm: LLM | None = None) -> Agent:
    """
    Instantiate and return Agent 3: Source Analyst.
    Focuses on critical source evaluation, extraction of metrics, and evidence mapping.
    """
    config = _load_analyst_config()
    active_llm = llm or get_crewai_llm()

    return Agent(
        role=config.get("role", "Senior Evidence & Source Analyst"),
        goal=config.get("goal", "Analyze collected sources, extract verifiable claims, and structure evidence."),
        backstory=config.get("backstory", "A meticulous intelligence and source evaluation analyst."),
        llm=active_llm,
        verbose=True,
        allow_delegation=False,
        tools=[],  # Dedicated to analytical evaluation of retrieved documents
    )

"""
agents/manager_agent.py - Agent 1: Research Manager.

Responsibilities:
- Understand the user's research topic.
- Create a structured research plan.
- Break the topic into targeted research questions and subtopics.
- Decide what areas require investigation.
- Coordinate the overall workflow.
- Passes a clear research plan to the research agents.
- Does NOT conduct web searches directly or write the final report.
"""

from __future__ import annotations

from typing import Any
import yaml
from pathlib import Path

from crewai import Agent, LLM
from api import get_crewai_llm


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agents.yaml"


def _load_manager_config() -> dict[str, Any]:
    """Load research manager configuration from config/agents.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "research_manager" in data:
                return data["research_manager"]
    return {
        "role": "Senior Research Project Manager",
        "goal": "Deconstruct research topics into structured, prioritized research plans.",
        "backstory": "An elite research director who structures complex inquiries into actionable subtopics."
    }


def create_research_manager_agent(llm: LLM | None = None) -> Agent:
    """
    Instantiate and return Agent 1: Research Manager.
    Focuses strictly on planning, subtopic decomposition, and strategy.
    """
    config = _load_manager_config()
    active_llm = llm or get_crewai_llm()

    return Agent(
        role=config.get("role", "Senior Research Project Manager"),
        goal=config.get("goal", "Deconstruct research topics into structured research plans."),
        backstory=config.get("backstory", "An elite research director and strategic planner."),
        llm=active_llm,
        verbose=True,
        allow_delegation=False,
        tools=[],  # Dedicated to planning; does not execute web queries
    )

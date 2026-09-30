"""
agents/researcher_agent.py - Agent 2: Web Researcher.

Responsibilities:
- Perform real web research using the Tavily web research tool.
- Search multiple relevant queries across the subtopics.
- Collect relevant, authoritative, and recent sources.
- Prioritize reports, government agencies, universities, and official docs.
- Preserve original source URL, title, publisher/domain, publication date, and snippet.
- Must NOT pretend that it searched the web; MUST use the Tavily tool.
"""

from __future__ import annotations

from typing import Any, Sequence
import yaml
from pathlib import Path

from crewai import Agent, LLM
from crewai.tools import BaseTool
from api import get_crewai_llm
from tools.tavily_search_tool import TavilySearchTool


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agents.yaml"


def _load_researcher_config() -> dict[str, Any]:
    """Load web researcher configuration from config/agents.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "web_researcher" in data:
                return data["web_researcher"]
    return {
        "role": "Lead Web Research Investigator",
        "goal": "Execute live web searches using Tavily to retrieve authoritative sources and evidence.",
        "backstory": "An expert digital research investigator who captures complete provenance for every source."
    }


def create_web_researcher_agent(
    llm: LLM | None = None,
    tools: Sequence[BaseTool] | None = None
) -> Agent:
    """
    Instantiate and return Agent 2: Web Researcher.
    Equipped with Tavily web research tool for real-time live internet investigation.
    """
    config = _load_researcher_config()
    active_llm = llm or get_crewai_llm()
    active_tools = list(tools) if tools is not None else [TavilySearchTool()]

    return Agent(
        role=config.get("role", "Lead Web Research Investigator"),
        goal=config.get("goal", "Execute live web searches using Tavily to retrieve authoritative sources."),
        backstory=config.get("backstory", "An expert digital investigator dedicated to factual accuracy."),
        llm=active_llm,
        tools=active_tools,
        verbose=True,
        allow_delegation=False,
    )

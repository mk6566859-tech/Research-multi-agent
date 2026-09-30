"""
agents/fact_checker_agent.py - Agent 4: Fact Checker.

Responsibilities:
- Verify important factual claims and statistics.
- Re-search questionable, conflicting, or surprising claims using Tavily.
- Compare conflicting information across independent sources.
- Identify and flag unsupported assertions or hallucinations.
- Prefer primary and authoritative sources (.gov, .edu, official reports).
- Mark uncertainty clearly (VERIFIED, CONTESTED, UNCERTAIN).
- Ensure statistics remain attached to their actual verified source.
- Preserve URLs and source metadata.
- MUST use a real search tool; must not merely guess or ask if a claim sounds correct.
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


def _load_fact_checker_config() -> dict[str, Any]:
    """Load fact checker configuration from config/agents.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "fact_checker" in data:
                return data["fact_checker"]
    return {
        "role": "Independent Fact-Checking & Verification Specialist",
        "goal": "Verify factual claims, re-search questionable assertions using Tavily, and guarantee source integrity.",
        "backstory": "An uncompromising editorial fact-checker with zero tolerance for hallucinations."
    }


def create_fact_checker_agent(
    llm: LLM | None = None,
    tools: Sequence[BaseTool] | None = None
) -> Agent:
    """
    Instantiate and return Agent 4: Fact Checker.
    Equipped with Tavily web research tool for independent corroboration and verification.
    """
    config = _load_fact_checker_config()
    active_llm = llm or get_crewai_llm()
    active_tools = list(tools) if tools is not None else [TavilySearchTool()]

    return Agent(
        role=config.get("role", "Independent Fact-Checking & Verification Specialist"),
        goal=config.get("goal", "Verify factual claims, re-search questionable assertions using Tavily, and guarantee source integrity."),
        backstory=config.get("backstory", "An uncompromising editorial fact-checker with zero tolerance for hallucinations."),
        llm=active_llm,
        tools=active_tools,
        verbose=True,
        allow_delegation=False,
    )

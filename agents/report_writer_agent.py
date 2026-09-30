"""
agents/report_writer_agent.py - Agent 5: Report Writer.

Responsibilities:
- Use ONLY the research evidence supplied by the previous agents.
- Produce the final executive-grade research report.
- Organize the report professionally with clear Markdown headers.
- Use inline numbered citations (e.g., [1], [2], [1][3]) throughout the text.
- Provide a complete numbered source list at the conclusion.
- Never invent citations, URLs, or study findings.
- Clearly distinguish factual evidence from analytical discussion.
- Mention uncertainty when the evidence is inconclusive.
- Grounded strictly in the research outputs.
"""

from __future__ import annotations

from typing import Any
import yaml
from pathlib import Path

from crewai import Agent, LLM
from api import get_crewai_llm


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agents.yaml"


def _load_writer_config() -> dict[str, Any]:
    """Load report writer configuration from config/agents.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "report_writer" in data:
                return data["report_writer"]
    return {
        "role": "Principal Research Report Writer & Synthesizer",
        "goal": "Synthesize verified evidence into an executive research report with strict citations [1], [2] and sources.",
        "backstory": "An award-winning research journalist who crafts lucid, deeply cited publications without fabricating facts."
    }


def create_report_writer_agent(llm: LLM | None = None) -> Agent:
    """
    Instantiate and return Agent 5: Report Writer.
    Focuses on comprehensive report synthesis, clear structure, and strict citation grounding.
    """
    config = _load_writer_config()
    active_llm = llm or get_crewai_llm()

    return Agent(
        role=config.get("role", "Principal Research Report Writer & Synthesizer"),
        goal=config.get("goal", "Synthesize verified evidence into an executive research report with strict citations [1], [2]."),
        backstory=config.get("backstory", "An award-winning research journalist and synthesis expert."),
        llm=active_llm,
        verbose=True,
        allow_delegation=False,
        tools=[],  # Synthesis is grounded exclusively in the evidence dossier
    )

"""
tasks/research_task.py - Task 2: Live Web Research Execution.

Assignee: Agent 2 (Web Researcher)
Objective: Execute web searches using Tavily, collect authoritative sources, and record full metadata.
"""

from __future__ import annotations

from typing import Any, Sequence
import yaml
from pathlib import Path

from crewai import Agent, Task


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "tasks.yaml"


def _load_task_config() -> dict[str, Any]:
    """Load research execution task configuration from config/tasks.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "research_task" in data:
                return data["research_task"]
    return {
        "description": "Execute live web searches using Tavily for '{topic}'. Collect authoritative sources and preserve metadata.",
        "expected_output": "A raw research dossier featuring 6 to 12 distinct, high-quality sources with URLs, titles, and snippets."
    }


def create_research_task(
    agent: Agent,
    topic: str,
    context: Sequence[Task] | None = None,
) -> Task:
    """
    Create Task 2: Web Research Execution.
    Orchestrated by the Web Researcher.
    """
    cfg = _load_task_config()
    desc_template = cfg.get("description", "Execute research for '{topic}' using Tavily.")
    out_template = cfg.get("expected_output", "Raw research dossier with full source provenance.")

    description = desc_template.format(topic=topic)

    return Task(
        description=description,
        expected_output=out_template,
        agent=agent,
        context=list(context) if context else [],
    )

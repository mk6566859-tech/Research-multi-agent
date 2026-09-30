"""
tasks/research_plan_task.py - Task 1: Research Plan Deconstruction.

Assignee: Agent 1 (Research Manager)
Objective: Deconstruct topic into 3-5 subtopics, define search queries and recency criteria.
"""

from __future__ import annotations

from typing import Any
import yaml
from pathlib import Path

from crewai import Agent, Task


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "tasks.yaml"


def _load_task_config() -> dict[str, Any]:
    """Load research plan task configuration from config/tasks.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "research_plan_task" in data:
                return data["research_plan_task"]
    return {
        "description": "Analyze '{topic}' with depth '{research_depth}' and focus '{focus_area}'. Break into 3-5 subtopics.",
        "expected_output": "A structured research blueprint detailing subtopics, queries, and recency requirements."
    }


def create_research_plan_task(
    agent: Agent,
    topic: str,
    research_depth: str = "Standard",
    focus_area: str = "General Web",
) -> Task:
    """
    Create Task 1: Research Plan.
    Orchestrated by the Research Manager.
    """
    cfg = _load_task_config()
    desc_template = cfg.get("description", "Analyze topic '{topic}' and create research plan.")
    out_template = cfg.get("expected_output", "Structured research plan.")

    description = desc_template.format(
        topic=topic,
        research_depth=research_depth,
        focus_area=focus_area,
    )

    return Task(
        description=description,
        expected_output=out_template,
        agent=agent,
    )

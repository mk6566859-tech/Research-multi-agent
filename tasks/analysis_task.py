"""
tasks/analysis_task.py - Task 3: Evidence Analysis and Mapping.

Assignee: Agent 3 (Source Analyst)
Objective: Extract facts, metrics, and claims from collected sources, assess reliability, and map claims to Source IDs.
"""

from __future__ import annotations

from typing import Any, Sequence
import yaml
from pathlib import Path

from crewai import Agent, Task


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "tasks.yaml"


def _load_task_config() -> dict[str, Any]:
    """Load source analysis task configuration from config/tasks.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "analysis_task" in data:
                return data["analysis_task"]
    return {
        "description": "Analyze collected sources for '{topic}'. Extract claims, evaluate reliability, and preserve Source IDs and URLs.",
        "expected_output": "A structured Evidence Matrix mapping subtopics to claims, metrics, and source URLs."
    }


def create_analysis_task(
    agent: Agent,
    topic: str,
    context: Sequence[Task] | None = None,
) -> Task:
    """
    Create Task 3: Evidence Analysis & Mapping.
    Orchestrated by the Source Analyst.
    """
    cfg = _load_task_config()
    desc_template = cfg.get("description", "Analyze sources for '{topic}'.")
    out_template = cfg.get("expected_output", "Structured Evidence Matrix.")

    description = desc_template.format(topic=topic)

    return Task(
        description=description,
        expected_output=out_template,
        agent=agent,
        context=list(context) if context else [],
    )

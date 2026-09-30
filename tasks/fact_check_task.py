"""
tasks/fact_check_task.py - Task 4: Fact-Checking and Verification.

Assignee: Agent 4 (Fact Checker)
Objective: Cross-examine claims, re-search questionable data using Tavily, classify verification status, and create verified source index.
"""

from __future__ import annotations

from typing import Any, Sequence
import yaml
from pathlib import Path

from crewai import Agent, Task


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "tasks.yaml"


def _load_task_config() -> dict[str, Any]:
    """Load fact check task configuration from config/tasks.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "fact_check_task" in data:
                return data["fact_check_task"]
    return {
        "description": "Cross-examine claims and statistics for '{topic}'. Re-search questionable claims via Tavily. Assign reference numbers [1], [2].",
        "expected_output": "A Verified Evidence Dossier with verified findings, resolved discrepancies, and master source index."
    }


def create_fact_check_task(
    agent: Agent,
    topic: str,
    context: Sequence[Task] | None = None,
) -> Task:
    """
    Create Task 4: Fact-Checking & Verification.
    Orchestrated by the Fact Checker.
    """
    cfg = _load_task_config()
    desc_template = cfg.get("description", "Fact check evidence for '{topic}'.")
    out_template = cfg.get("expected_output", "Verified Evidence Dossier with master source index.")

    description = desc_template.format(topic=topic)

    return Task(
        description=description,
        expected_output=out_template,
        agent=agent,
        context=list(context) if context else [],
    )

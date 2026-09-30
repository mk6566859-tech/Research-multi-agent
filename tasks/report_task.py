"""
tasks/report_task.py - Task 5: Final Cited Research Report Generation.

Assignee: Agent 5 (Report Writer)
Objective: Synthesize the final comprehensive research report strictly from verified evidence,
with inline numbered citations [1], [2] and an unhallucinated sources section.
"""

from __future__ import annotations

from typing import Any, Sequence
import yaml
from pathlib import Path

from crewai import Agent, Task


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "tasks.yaml"


def _load_task_config() -> dict[str, Any]:
    """Load report task configuration from config/tasks.yaml."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if "report_task" in data:
                return data["report_task"]
    return {
        "description": "Synthesize the final research report on '{topic}' using inline citations [1], [2] and real URLs.",
        "expected_output": "A publication-grade Markdown research report with inline citations and a complete '### Sources' section."
    }


def create_report_task(
    agent: Agent,
    topic: str,
    context: Sequence[Task] | None = None,
) -> Task:
    """
    Create Task 5: Final Report Generation.
    Orchestrated by the Report Writer.
    """
    cfg = _load_task_config()
    desc_template = cfg.get("description", "Synthesize report for '{topic}'.")
    out_template = cfg.get("expected_output", "Complete Markdown report with inline citations and sources.")

    description = desc_template.format(topic=topic)

    return Task(
        description=description,
        expected_output=out_template,
        agent=agent,
        context=list(context) if context else [],
    )

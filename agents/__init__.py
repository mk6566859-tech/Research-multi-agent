"""
agents package - Multi-agent definitions for ResearchPilot AI.
"""

from agents.manager_agent import create_research_manager_agent
from agents.researcher_agent import create_web_researcher_agent
from agents.source_analyst_agent import create_source_analyst_agent
from agents.fact_checker_agent import create_fact_checker_agent
from agents.report_writer_agent import create_report_writer_agent

__all__ = [
    "create_research_manager_agent",
    "create_web_researcher_agent",
    "create_source_analyst_agent",
    "create_fact_checker_agent",
    "create_report_writer_agent",
]

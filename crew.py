"""
crew.py - CrewAI Multi-Agent Orchestration for ResearchPilot AI.

Assembles the 5 specialized agents and 5 sequential tasks into an end-to-end
research pipeline, executes live web investigations via Tavily, coordinates
factual verification, and aligns final inline citations with recorded sources.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from crewai import Crew, Process
from crewai.hooks.llm_hooks import (
    register_before_llm_call_hook,
    unregister_before_llm_call_hook,
)

from api import get_crewai_llm, validate_api_keys
from agents import (
    create_research_manager_agent,
    create_web_researcher_agent,
    create_source_analyst_agent,
    create_fact_checker_agent,
    create_report_writer_agent,
)
from tasks import (
    create_research_plan_task,
    create_research_task,
    create_analysis_task,
    create_fact_check_task,
    create_report_task,
)
from tools.source_utils import GLOBAL_SOURCE_REGISTRY, SourceRecord
from tools.citation_utils import verify_and_align_report
from tools.groq_compat import strip_cache_breakpoints
from tools.tavily_search_tool import TavilySearchTool


logger = logging.getLogger(__name__)


def _remove_unsupported_cache_breakpoints(context: Any) -> None:
    strip_cache_breakpoints(context.messages)


@dataclass
class ResearchResult:
    """Encapsulates the final synthesized research report and its metadata."""
    topic: str
    report_markdown: str
    sources: list[SourceRecord] = field(default_factory=list)
    citations: list[dict[str, Any]] = field(default_factory=list)
    raw_output: str = ""
    success: bool = True
    error_message: str | None = None


class ResearchPilotCrew:
    """
    Coordinates the 5-agent sequential research workflow:
    Research Manager -> Web Researcher -> Source Analyst -> Fact Checker -> Report Writer
    """

    def __init__(
        self,
        model_name: str | None = None,
        research_depth: str = "Standard",
        focus_area: str = "General Web",
    ):
        self.model_name = model_name
        self.research_depth = research_depth
        self.focus_area = focus_area

    def run(self, topic: str) -> ResearchResult:
        """
        Execute the full research pipeline on the provided topic.

        Args:
            topic: The research question or subject entered by the user.

        Returns:
            ResearchResult with the final report, verified sources, and citation metadata.
        """
        clean_topic = topic.strip()
        if not clean_topic:
            return ResearchResult(
                topic=topic,
                report_markdown="",
                success=False,
                error_message="Please provide a valid, non-empty research topic."
            )

        # 1. Validate API credentials before launching the multi-agent run
        valid, msg = validate_api_keys()
        if not valid:
            return ResearchResult(
                topic=clean_topic,
                report_markdown="",
                success=False,
                error_message=msg,
            )

        # 2. Reset session source registry for clean provenance
        GLOBAL_SOURCE_REGISTRY.clear()

        try:
            # 3. Initialize centralized Groq LLM
            llm = get_crewai_llm(model_name=self.model_name)

            # 4. Initialize cloud-based Tavily search tool
            tavily_depth = "advanced" if self.research_depth.lower() == "deep" else "basic"
            max_res = 8 if self.research_depth.lower() == "deep" else 5
            search_tool = TavilySearchTool(search_depth=tavily_depth, max_results=max_res)

            # 5. Build the 5 specialized agents
            manager_agent = create_research_manager_agent(llm=llm)
            researcher_agent = create_web_researcher_agent(llm=llm, tools=[search_tool])
            analyst_agent = create_source_analyst_agent(llm=llm)
            fact_checker_agent = create_fact_checker_agent(llm=llm, tools=[search_tool])
            writer_agent = create_report_writer_agent(llm=llm)

            # 6. Build the 5 sequential tasks with explicit context linking
            plan_task = create_research_plan_task(
                agent=manager_agent,
                topic=clean_topic,
                research_depth=self.research_depth,
                focus_area=self.focus_area,
            )

            research_task = create_research_task(
                agent=researcher_agent,
                topic=clean_topic,
                context=[plan_task],
            )

            analysis_task = create_analysis_task(
                agent=analyst_agent,
                topic=clean_topic,
                context=[research_task],
            )

            fact_check_task = create_fact_check_task(
                agent=fact_checker_agent,
                topic=clean_topic,
                context=[analysis_task, research_task],
            )

            report_task = create_report_task(
                agent=writer_agent,
                topic=clean_topic,
                context=[fact_check_task, analysis_task],
            )

            # 7. Assemble the Crew
            crew = Crew(
                agents=[
                    manager_agent,
                    researcher_agent,
                    analyst_agent,
                    fact_checker_agent,
                    writer_agent,
                ],
                tasks=[
                    plan_task,
                    research_task,
                    analysis_task,
                    fact_check_task,
                    report_task,
                ],
                process=Process.sequential,
                verbose=True,
                memory=False,
                cache=False,
            )

            # LiteLLM's Groq adapter forwards CrewAI's internal marker as an
            # API message property; Groq rejects it, so strip it before each call.
            register_before_llm_call_hook(_remove_unsupported_cache_breakpoints)
            try:
                crew_output = crew.kickoff(
                    inputs={
                        "topic": clean_topic,
                        "research_depth": self.research_depth,
                        "focus_area": self.focus_area,
                    }
                )
            finally:
                unregister_before_llm_call_hook(_remove_unsupported_cache_breakpoints)

            raw_text = str(crew_output.raw) if hasattr(crew_output, "raw") else str(crew_output)

            # 9. Verify and align citations against recorded sources
            collected_sources = GLOBAL_SOURCE_REGISTRY.get_all()
            final_report, citation_meta = verify_and_align_report(raw_text, collected_sources)

            return ResearchResult(
                topic=clean_topic,
                report_markdown=final_report,
                sources=collected_sources,
                citations=citation_meta,
                raw_output=raw_text,
                success=True,
            )

        except Exception as exc:
            err_msg = str(exc)
            logger.exception(f"Multi-agent research pipeline failed: {err_msg}")
            return ResearchResult(
                topic=clean_topic,
                report_markdown="",
                success=False,
                error_message=f"Research workflow failed: {err_msg}",
            )

"""
tools/tavily_search_tool.py - Cloud-based Tavily Search Tool for CrewAI agents.

Executes live remote searches via the official Tavily Python SDK, extracts structured
source records, stores them in the global source registry, and provides formatted
evidence to the research agents.
"""

from __future__ import annotations

import logging
from typing import Any, Type
from pydantic import BaseModel, Field

from crewai.tools import BaseTool
from tools.source_utils import GLOBAL_SOURCE_REGISTRY, normalize_url, extract_domain


logger = logging.getLogger(__name__)


class TavilySearchInput(BaseModel):
    """Input schema for the Tavily web search tool."""
    query: str = Field(
        ...,
        description="The precise search query to execute on the live web (e.g., 'generative AI cybersecurity trends 2026')."
    )


class TavilySearchTool(BaseTool):
    """
    CrewAI BaseTool that connects to Tavily's remote search API to perform
    real-time, authoritative web research without requiring any local browser or driver.
    """
    name: str = "tavily_web_search"
    description: str = (
        "Search the live web for authoritative sources, studies, reports, statistics, "
        "and factual evidence on any topic. Returns structured source records including "
        "source ID, document title, exact URL, domain, publication date, and content snippet."
    )
    args_schema: Type[BaseModel] = TavilySearchInput
    api_key: str | None = None
    search_depth: str = "basic"
    max_results: int = 5
    include_domains: list[str] | None = None

    def __init__(
        self,
        api_key: str | None = None,
        search_depth: str = "basic",
        max_results: int = 5,
        include_domains: list[str] | None = None,
        **kwargs: Any
    ):
        super().__init__(
            api_key=api_key,
            search_depth=search_depth,
            max_results=max_results,
            include_domains=include_domains,
            **kwargs
        )

    def _get_api_key(self) -> str:
        """Resolve API key from instance or central api module."""
        if self.api_key:
            return self.api_key
        from api import get_tavily_api_key
        return get_tavily_api_key()

    def _run(self, query: str) -> str:
        """Execute web search using Tavily API and return structured evidence."""
        query = query.strip()
        if not query:
            return "Error: Empty search query provided."

        try:
            from tavily import TavilyClient
        except ImportError:
            return "Error: 'tavily-python' package is not installed. Please install tavily-python."

        try:
            key = self._get_api_key()
        except Exception as e:
            return f"Error: Tavily API key could not be loaded: {str(e)}"

        try:
            client = TavilyClient(api_key=key)

            search_kwargs: dict[str, Any] = {
                "query": query,
                "search_depth": self.search_depth,
                "max_results": self.max_results,
            }
            if self.include_domains:
                search_kwargs["include_domains"] = self.include_domains

            response = client.search(**search_kwargs)
            results = response.get("results", [])

            if not results:
                return f"No results found on the live web for query: '{query}'. Try broader terms or synonyms."

            output_lines = [f"### Web Search Results for: '{query}' ({len(results)} sources retrieved)\n"]

            for r in results:
                raw_url = r.get("url", "")
                title = r.get("title", "Untitled Web Document")
                content = r.get("content", "")
                pub_date = r.get("published_date")
                score = r.get("score")

                # Record in global session registry for citation mapping
                record = GLOBAL_SOURCE_REGISTRY.add_source(
                    url=raw_url,
                    title=title,
                    content=content,
                    published_date=pub_date,
                    score=score,
                    query=query,
                )

                output_lines.append(record.to_agent_format())
                output_lines.append("---")

            return "\n".join(output_lines)

        except Exception as exc:
            error_msg = str(exc)
            logger.error(f"Tavily search failed for query '{query}': {error_msg}")
            return f"Search execution encountered an error: {error_msg}. Please rephrase or use alternative terms."

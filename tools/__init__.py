"""
tools package - External API tools, source processing, and citation helpers.
"""

from tools.source_utils import SourceRecord, SourceRegistry, GLOBAL_SOURCE_REGISTRY, normalize_url, extract_domain
from tools.citation_utils import extract_inline_citations, generate_sources_section, verify_and_align_report
from tools.tavily_search_tool import TavilySearchTool

__all__ = [
    "SourceRecord",
    "SourceRegistry",
    "GLOBAL_SOURCE_REGISTRY",
    "normalize_url",
    "extract_domain",
    "extract_inline_citations",
    "generate_sources_section",
    "verify_and_align_report",
    "TavilySearchTool",
]

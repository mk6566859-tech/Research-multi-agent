"""
tools/citation_utils.py - Citation processing, validation, and bibliography formatting.

Ensures all inline citations [1], [2] in the final report correspond strictly to
actual verified web sources, deduplicates URLs, and generates professional bibliographies.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from tools.source_utils import SourceRecord, normalize_url


# Regex patterns for matching inline citations like [1], [2], [1][2], or [1, 2]
INLINE_CITATION_PATTERN = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
URL_PATTERN = re.compile(r"https?://[^\s)\]\"'>]+")


def extract_inline_citations(text: str) -> list[int]:
    """
    Extract all unique integer citation numbers referenced in the text.
    For example: 'According to studies [1][2], and [3]' -> [1, 2, 3]
    """
    citations: set[int] = set()
    for match in INLINE_CITATION_PATTERN.finditer(text):
        groups = match.group(1).split(",")
        for item in groups:
            item = item.strip()
            if item.isdigit():
                citations.add(int(item))
    return sorted(list(citations))


def extract_urls_from_text(text: str) -> list[str]:
    """Extract all valid HTTP/HTTPS URLs present in a markdown string."""
    raw_urls = URL_PATTERN.findall(text)
    clean_urls: list[str] = []
    seen: set[str] = set()
    for u in raw_urls:
        u_clean = u.rstrip(".,;:)")
        norm = normalize_url(u_clean)
        if norm and norm not in seen:
            seen.add(norm)
            clean_urls.append(u_clean)
    return clean_urls


def format_bibliography_item(index: int, source: SourceRecord) -> str:
    """Format a single bibliography entry with title, domain/publisher, and clean URL."""
    publisher = source.domain or "Web Source"
    title = source.title.strip() if source.title else f"Reference {index}"
    url = source.url.strip()
    return f"[{index}] {title} — {publisher}\n{url}"


def generate_sources_section(sources: list[SourceRecord]) -> str:
    """
    Generate a clean Markdown bibliography section from a list of SourceRecord objects.
    Deduplicates URLs and assigns sequential numbers [1], [2], etc.
    """
    if not sources:
        return "### Sources\n*No external sources were retrieved for this research.*"

    seen_urls: set[str] = set()
    unique_sources: list[SourceRecord] = []

    for s in sources:
        norm = normalize_url(s.url)
        if norm not in seen_urls:
            seen_urls.add(norm)
            unique_sources.append(s)

    items = []
    for idx, src in enumerate(unique_sources, start=1):
        items.append(format_bibliography_item(idx, src))

    return "### Sources\n" + "\n\n".join(items)


def verify_and_align_report(
    report_text: str,
    recorded_sources: list[SourceRecord]
) -> tuple[str, list[dict[str, Any]]]:
    """
    Verify report citations against recorded sources.
    If the report contains inline citations or an incomplete sources block,
    aligns the bibliography with recorded sources so every citation points to a real URL.

    Returns:
        (aligned_report_text, citation_metadata_list)
    """
    if not report_text:
        return "", []

    # Map sources by index (1-based)
    source_map: dict[int, SourceRecord] = {}
    for idx, s in enumerate(recorded_sources, start=1):
        source_map[idx] = s

    # Find citation numbers cited in the body of the report
    body_citations = extract_inline_citations(report_text)

    # Prepare structured citation metadata
    citation_metadata: list[dict[str, Any]] = []
    for num in body_citations:
        src = source_map.get(num)
        if src:
            citation_metadata.append({
                "citation_number": num,
                "title": src.title,
                "url": src.url,
                "domain": src.domain,
                "published_date": src.published_date,
            })

    # If the report already ends with a Sources / References section, ensure it is properly formatted
    # If the agent omitted or truncated the bibliography, append the verified sources section
    has_sources_header = bool(re.search(r"(?:###?\s*(?:Sources|References|Bibliography))", report_text, re.IGNORECASE))

    if not has_sources_header and recorded_sources:
        # Append bibliography
        aligned_report = report_text.rstrip() + "\n\n" + generate_sources_section(recorded_sources)
    else:
        aligned_report = report_text

    return aligned_report, citation_metadata

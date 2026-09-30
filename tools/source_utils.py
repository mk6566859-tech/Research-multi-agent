"""
tools/source_utils.py - Source data structures, URL normalization, and metadata handling.

Provides structured source representation, deduplication, domain extraction, and
in-memory source tracking for the multi-agent research workflow.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


# Tracking query parameters to strip for clean URL normalization
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "msclkid", "ref", "source", "mc_cid", "mc_eid"
}

# Authoritative domain suffixes and known credible institutional domains
AUTHORITATIVE_TLDS = (".gov", ".edu", ".mil")
AUTHORITATIVE_DOMAINS = {
    "nature.com", "science.org", "sciencedirect.com", "arxiv.org", "ieee.org",
    "acm.org", "nih.gov", "cdc.gov", "who.int", "un.org", "worldbank.org",
    "imf.org", "oecd.org", "reuters.com", "bloomberg.com", "ft.com",
    "wsj.com", "apnews.com", "bbc.com", "mit.edu", "stanford.edu", "harvard.edu"
}


def normalize_url(url: str) -> str:
    """
    Clean and normalize a URL by stripping tracking parameters, normalizing schemes,
    and removing trailing slashes.
    """
    if not url or not isinstance(url, str):
        return ""

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        # Filter out tracking query parameters
        filtered_queries = [
            (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=False)
            if k.lower() not in TRACKING_PARAMS
        ]
        new_query = urlencode(filtered_queries)

        path = parsed.path.rstrip("/")
        if not path and not new_query:
            path = ""

        clean_url = urlunparse((scheme, netloc, path, parsed.params, new_query, ""))
        return clean_url
    except Exception:
        return url.rstrip("/")


def extract_domain(url: str) -> str:
    """Extract clean domain name from a URL (e.g., 'reuters.com')."""
    if not url:
        return "unknown"
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain or "unknown"
    except Exception:
        return "unknown"


def is_authoritative(domain: str) -> bool:
    """Check if domain represents an authoritative, academic, or governmental source."""
    if not domain:
        return False
    domain_lower = domain.lower()
    if any(domain_lower.endswith(tld) for tld in AUTHORITATIVE_TLDS):
        return True
    return any(domain_lower == auth or domain_lower.endswith("." + auth) for auth in AUTHORITATIVE_DOMAINS)


@dataclass
class SourceRecord:
    """Structured representation of a single web research source."""
    source_id: str
    url: str
    title: str
    domain: str = ""
    content: str = ""
    published_date: str | None = None
    score: float | None = None
    query: str | None = None

    def __post_init__(self):
        if not self.domain and self.url:
            self.domain = extract_domain(self.url)
        if not self.title or self.title.strip() == "":
            self.title = f"Document from {self.domain}"

    @property
    def clean_url(self) -> str:
        return normalize_url(self.url)

    def to_agent_format(self) -> str:
        """Format source details for injection into LLM agent prompts."""
        lines = [
            f"Source ID: [{self.source_id}]",
            f"Title: {self.title}",
            f"Domain: {self.domain}",
            f"URL: {self.url}",
        ]
        if self.published_date:
            lines.append(f"Published Date: {self.published_date}")
        if self.content:
            clean_snippet = re.sub(r"\s+", " ", self.content.strip())
            lines.append(f"Content Snippet: {clean_snippet}")
        return "\n".join(lines)


class SourceRegistry:
    """
    Session-level registry for tracking, deduplicating, and referencing web sources.
    """

    def __init__(self):
        self._sources: list[SourceRecord] = []
        self._url_to_source: dict[str, SourceRecord] = {}

    def add_source(
        self,
        url: str,
        title: str,
        content: str,
        published_date: str | None = None,
        score: float | None = None,
        query: str | None = None,
    ) -> SourceRecord:
        """Add a source if not already present; returns existing or new SourceRecord."""
        norm_url = normalize_url(url)
        if not norm_url:
            norm_url = url.strip()

        if norm_url in self._url_to_source:
            existing = self._url_to_source[norm_url]
            # Augment snippet if existing is short
            if len(content) > len(existing.content):
                existing.content = content
            if not existing.published_date and published_date:
                existing.published_date = published_date
            return existing

        next_idx = len(self._sources) + 1
        source_id = f"S{next_idx}"
        record = SourceRecord(
            source_id=source_id,
            url=url.strip(),
            title=title.strip() if title else f"Source {next_idx}",
            domain=extract_domain(url),
            content=content,
            published_date=published_date,
            score=score,
            query=query,
        )
        self._sources.append(record)
        self._url_to_source[norm_url] = record
        return record

    def get_all(self) -> list[SourceRecord]:
        return list(self._sources)

    def count(self) -> int:
        return len(self._sources)

    def clear(self):
        self._sources.clear()
        self._url_to_source.clear()

    def format_all_for_agent(self) -> str:
        """Render all recorded sources into a clear text dossier for agents."""
        if not self._sources:
            return "No web sources recorded."
        records_str = "\n\n---\n".join(s.to_agent_format() for s in self._sources)
        return f"### Recorded Web Sources ({len(self._sources)} total)\n\n---\n{records_str}\n---"


# Global singleton registry instance for easy cross-module recording
GLOBAL_SOURCE_REGISTRY = SourceRegistry()

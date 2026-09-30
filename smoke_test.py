"""
smoke_test.py - Automated smoke test suite for ResearchPilot AI.

Validates:
1. Module imports and file linkages.
2. Source normalization, deduplication, and domain extraction.
3. Inline citation parsing and bibliography generation.
4. Model identifier formatting and API validation safeguards.
5. Multi-agent and task factory instantiation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_smoke_tests():
    print("=" * 60)
    print("[*] ResearchPilot AI - Smoke Test Suite")
    print("=" * 60)

    # 1. Test Source Utilities
    print("\n[Test 1] Testing source utilities and URL normalization...")
    from tools.source_utils import (
        normalize_url,
        extract_domain,
        is_authoritative,
        SourceRegistry,
        SourceRecord,
    )

    dirty_url = "https://www.reuters.com/technology/ai-breakthrough/?utm_source=twitter&utm_medium=social&ref=123"
    clean_url = normalize_url(dirty_url)
    assert clean_url == "https://reuters.com/technology/ai-breakthrough", f"Unexpected clean URL: {clean_url}"
    print(f"  ✓ URL normalization passed: '{dirty_url}' -> '{clean_url}'")

    domain = extract_domain(clean_url)
    assert domain == "reuters.com", f"Unexpected domain: {domain}"
    assert is_authoritative(domain) is True, "reuters.com should be recognized as authoritative"
    print(f"  ✓ Domain extraction and authority check passed: '{domain}'")

    registry = SourceRegistry()
    s1 = registry.add_source(
        url="https://reuters.com/ai",
        title="AI Advancements",
        content="Generative AI adoption is growing across industries.",
        published_date="2026-01-15",
    )
    s2 = registry.add_source(
        url="https://reuters.com/ai/?utm_source=newsletter",  # Duplicate with tracking
        title="AI Advancements (Dup)",
        content="Longer content snippet showing deeper findings.",
    )
    assert registry.count() == 1, f"Expected 1 unique source after deduplication, got {registry.count()}"
    assert s1.source_id == "S1"
    print("  ✓ Source registry deduplication passed.")

    # 2. Test Citation Utilities
    print("\n[Test 2] Testing citation utilities and bibliography generation...")
    from tools.citation_utils import (
        extract_inline_citations,
        generate_sources_section,
        verify_and_align_report,
    )

    sample_report = (
        "# AI Report\n\n"
        "AI improves cybersecurity operations [1]. "
        "It also brings new challenges in automated phishing detection [1][2]."
    )

    citations = extract_inline_citations(sample_report)
    assert citations == [1, 2], f"Expected citations [1, 2], got {citations}"
    print(f"  ✓ Inline citation extraction passed: {citations}")

    src_list = [
        SourceRecord(source_id="1", url="https://cisa.gov/ai", title="AI Security Guidelines", domain="cisa.gov"),
        SourceRecord(source_id="2", url="https://nist.gov/ai-risk", title="AI Risk Management Framework", domain="nist.gov"),
    ]
    biblio = generate_sources_section(src_list)
    assert "[1] AI Security Guidelines — cisa.gov" in biblio
    assert "[2] AI Risk Management Framework — nist.gov" in biblio
    print("  ✓ Bibliography generation passed.")

    aligned_text, meta = verify_and_align_report(sample_report, src_list)
    assert "### Sources" in aligned_text
    assert len(meta) == 2
    print("  ✓ Report alignment and verification passed.")

    # 3. Test Groq message compatibility
    print("\n[Test 3] Testing unsupported CrewAI cache metadata cleanup...")
    from tools.groq_compat import (
        MAX_GROQ_PROMPT_BYTES,
        TRUNCATION_MARKER,
        prepare_groq_messages,
    )

    messages = [
        {"role": "system", "content": "Instructions", "cache_breakpoint": True},
        {"role": "user", "content": "Research topic " * 1000, "cache_breakpoint": True},
        {"role": "assistant", "content": "Response"},
    ]
    prepare_groq_messages(messages)
    assert all("cache_breakpoint" not in message for message in messages)
    assert messages[0]["content"] == "Instructions"
    prompt_bytes = sum(
        len(message["content"].encode("utf-8"))
        for message in messages
        if isinstance(message.get("content"), str)
    )
    assert prompt_bytes <= MAX_GROQ_PROMPT_BYTES
    assert TRUNCATION_MARKER in messages[1]["content"]
    print("  ✓ Cache metadata removed and prompt bounded with content retained.")

    # 4. Test API Module
    print("\n[Test 4] Testing centralized API and model configurations...")
    from api import (
        GROQ_MAX_COMPLETION_TOKENS,
        format_groq_model_identifier,
        get_groq_model,
        validate_api_keys,
    )

    formatted_model = format_groq_model_identifier("openai/gpt-oss-120b")
    assert formatted_model == "groq/openai/gpt-oss-120b", f"Unexpected formatted model: {formatted_model}"
    print(f"  ✓ Groq model identifier formatting passed: {formatted_model}")
    assert GROQ_MAX_COMPLETION_TOKENS == 1024
    print(f"  ✓ Groq completion budget confirmed: {GROQ_MAX_COMPLETION_TOKENS} tokens")

    default_model = get_groq_model()
    assert default_model == "openai/gpt-oss-120b"
    print(f"  ✓ Default model confirmed: {default_model}")

    # Key validation returns boolean and friendly message without crash
    is_valid, msg = validate_api_keys()
    print(f"  ✓ API key validator returned: valid={is_valid}, msg='{msg}'")

    # 5. Test Agent and Task Construction
    print("\n[Test 5] Testing Agent and Task factory structures...")
    from agents.manager_agent import _load_manager_config
    from tasks.research_plan_task import _load_task_config

    mgr_cfg = _load_manager_config()
    assert "role" in mgr_cfg and "goal" in mgr_cfg
    print(f"  ✓ Agent YAML configuration loaded: {mgr_cfg['role']}")

    task_cfg = _load_task_config()
    assert "description" in task_cfg and "expected_output" in task_cfg
    print("  ✓ Task YAML configuration loaded.")

    print("\n" + "=" * 60)
    print("🎉 ALL SMOKE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_smoke_tests()
    except Exception as exc:
        print(f"\n❌ Smoke test failed: {exc}")
        sys.exit(1)

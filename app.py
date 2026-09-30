"""
app.py - Streamlit User Interface for ResearchPilot AI.

A clean, modern, beginner-friendly interface for running multi-agent
web research with Groq and Tavily.
"""

from __future__ import annotations

import streamlit as st
from datetime import datetime

from api import validate_api_keys, get_groq_model, get_secret
from crew import ResearchPilotCrew, ResearchResult


# Page configuration
st.set_page_config(
    page_title="ResearchPilot AI — Autonomous Multi-Agent Research Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished aesthetics
st.markdown(
    """
    <style>
    /* Modern UI refinements */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1E88E5, #7E57C2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .agent-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-ok {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .badge-missing {
        background-color: #ffebee;
        color: #c62828;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar():
    """Render sidebar controls, settings, and credentials status."""
    st.sidebar.title("⚙️ Configuration")

    # API Keys Status Check
    st.sidebar.markdown("### 🔑 API Status")
    groq_present = bool(get_secret("GROQ_API_KEY"))
    tavily_present = bool(get_secret("TAVILY_API_KEY"))

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if groq_present:
            st.markdown('<span class="status-badge badge-ok">✅ Groq Active</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge badge-missing">⚠️ Groq Key Missing</span>', unsafe_allow_html=True)
    with col2:
        if tavily_present:
            st.markdown('<span class="status-badge badge-ok">✅ Tavily Active</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge badge-missing">⚠️ Tavily Key Missing</span>', unsafe_allow_html=True)

    if not (groq_present and tavily_present):
        st.sidebar.warning(
            "Please configure your API keys in `.streamlit/secrets.toml` or your Streamlit Cloud Secrets settings."
        )

    st.sidebar.markdown("---")

    # Research depth selector
    depth = st.sidebar.select_slider(
        "🔎 Research Depth",
        options=["Quick", "Standard", "Deep"],
        value="Standard",
        help="Quick retrieves 3-5 sources with fast search. Deep executes advanced search with 8-12 sources.",
    )

    # Focus area selector
    focus = st.sidebar.selectbox(
        "🎯 Source Focus",
        options=[
            "General Web",
            "Academic / Research",
            "Government / Official",
            "Technology & Engineering",
            "Recent News & Developments",
        ],
        index=0,
        help="Guides the research manager and search tool to prioritize specific categories of sources.",
    )

    # Model info display
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Multi-Agent Engine")
    model_name = get_groq_model()
    st.sidebar.info(f"**LLM:** Groq ({model_name})\n\n**Framework:** CrewAI\n\n**Agents:** 5 Specialized Roles")

    st.sidebar.markdown(
        """
        **Workflow Pipeline:**
        1. 📋 **Research Manager** (Planning)
        2. 🌐 **Web Researcher** (Live Tavily Search)
        3. 🔬 **Source Analyst** (Evidence Matrix)
        4. ⚖️ **Fact Checker** (Verification)
        5. ✍️ **Report Writer** (Cited Report)
        """
    )

    return depth, focus, model_name


def main():
    # Sidebar
    depth, focus, model_name = render_sidebar()

    # Main header
    st.markdown('<div class="main-header">🧭 ResearchPilot AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Autonomous multi-agent research assistant powered by Groq, CrewAI, and Tavily. '
        'Delivers publication-grade reports with verifiable inline citations.</div>',
        unsafe_allow_html=True,
    )

    # Pre-flight API check banner
    is_valid, msg = validate_api_keys()
    if not is_valid:
        st.error(
            f"**Setup Required:** {msg}\n\n"
            "To use ResearchPilot AI, create a `.streamlit/secrets.toml` file (see `.streamlit/secrets.toml.example`) "
            "or add `GROQ_API_KEY` and `TAVILY_API_KEY` in the Streamlit Cloud Dashboard."
        )

    # Example topics for one-click discovery
    st.markdown("**💡 Or pick an example topic:**")
    example_cols = st.columns(3)
    preset_topic = ""
    if example_cols[0].button("🛡️ AI in Cybersecurity Trends", use_container_width=True):
        preset_topic = "Impact of Generative AI on Cybersecurity Defense and Phishing in 2026"
    if example_cols[1].button("🔋 Solid-State Battery Breakthroughs", use_container_width=True):
        preset_topic = "Recent Commercial Breakthroughs and Timelines in Solid-State Batteries"
    if example_cols[2].button("🧠 Open-Weights LLM Ecosystem", use_container_width=True):
        preset_topic = "Current State and Performance of Open-Weights Reasoning Models in 2026"

    # Research topic text input
    initial_value = preset_topic if preset_topic else ""
    user_topic = st.text_input(
        "Enter your research topic or question:",
        value=initial_value,
        placeholder="e.g., Global advances in nuclear fusion energy experiments and commercial targets",
    )

    start_button = st.button("🚀 Start Multi-Agent Research", type="primary", use_container_width=True)

    if start_button:
        if not user_topic.strip():
            st.warning("Please enter a research topic to begin.")
            return

        if not is_valid:
            st.error("Cannot start research: Missing API keys. Please configure them first.")
            return

        # Status & Progress Area
        status_container = st.status("🚀 Launching Multi-Agent Research Crew...", expanded=True)

        with status_container:
            st.write("📋 **Research Manager:** Deconstructing topic into subtopics and search parameters...")
            st.write("🌐 **Web Researcher:** Initializing Tavily web search agent...")
            st.write("🔬 **Source Analyst:** Preparing evidence matrix...")
            st.write("⚖️ **Fact Checker:** Setting up corroboration protocols...")
            st.write("✍️ **Report Writer:** Readying inline citation synthesizer...")

            try:
                # Orchestrate the multi-agent run
                crew_orchestrator = ResearchPilotCrew(
                    model_name=model_name,
                    research_depth=depth,
                    focus_area=focus,
                )

                result: ResearchResult = crew_orchestrator.run(user_topic)

                if not result.success:
                    status_container.update(label="❌ Research Failed", state="error", expanded=True)
                    st.error(result.error_message or "An unexpected error occurred during research.")
                    return

                status_container.update(
                    label=f"✅ Research Complete! ({len(result.sources)} sources analyzed and cited)",
                    state="complete",
                    expanded=False,
                )

                # Store result in session state
                st.session_state["latest_result"] = result

            except Exception as e:
                status_container.update(label="❌ Error Encountered", state="error", expanded=True)
                st.error(f"Execution Error: {str(e)}")
                return

    # Display results if present in session state
    if "latest_result" in st.session_state:
        result: ResearchResult = st.session_state["latest_result"]

        st.markdown("---")

        tab_report, tab_sources, tab_download = st.tabs([
            "📄 Research Report",
            f"🌐 Verified Sources ({len(result.sources)})",
            "💾 Export & Download",
        ])

        with tab_report:
            st.markdown(result.report_markdown)

        with tab_sources:
            if result.sources:
                st.markdown("### Verified Sources Directory")
                st.markdown(
                    "The following authentic web sources were collected, evaluated, and fact-checked "
                    "during the research run:"
                )
                for idx, src in enumerate(result.sources, start=1):
                    with st.expander(f"[{idx}] {src.title} ({src.domain})"):
                        st.markdown(f"**URL:** [{src.url}]({src.url})")
                        if src.published_date:
                            st.markdown(f"**Published Date:** {src.published_date}")
                        if src.content:
                            st.markdown(f"**Excerpted Evidence:**\n> {src.content}")
            else:
                st.info("No external web sources were recorded for this topic.")

        with tab_download:
            st.markdown("### Export Research Report")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ResearchReport_{timestamp}.md"

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📥 Download Report as Markdown (.md)",
                    data=result.report_markdown,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col_dl2:
                st.download_button(
                    label="📄 Download Report as Plain Text (.txt)",
                    data=result.report_markdown,
                    file_name=f"ResearchReport_{timestamp}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()

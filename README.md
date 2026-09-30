# 🧭 ResearchPilot AI — Autonomous Multi-Agent Research Assistant

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.15.23-orange.svg)](https://crewai.com)
[![Groq](https://img.shields.io/badge/Groq-Fast_Inference-green.svg)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-red.svg)](https://streamlit.io)

**ResearchPilot AI** is a professional, beginner-friendly multi-agent research application. It turns any research topic into an executive-grade, fully cited research report with authentic web sources, factual cross-checking, and zero hallucinations.

---

## 💡 What Does This Application Do?

Instead of relying on a single AI chatbot that might guess facts or invent fake URLs, **ResearchPilot AI** uses a collaborative team of **5 specialized AI agents**. 

Each agent works like an employee in a professional research organization:
1. **Plans the investigation** into clear research questions.
2. **Searches the live internet** using the official Tavily cloud search service.
3. **Analyzes and organizes evidence** by subtopic while tracking source IDs.
4. **Fact-checks claims and numbers** by re-searching live data to eliminate errors.
5. **Writes the final publication-grade report** with clickable inline citations like `[1]`, `[2]` and a complete, real bibliography.

---

## 🏛️ System Architecture

```
User Topic Input (Streamlit UI)
      │
      ▼
Agent 1: Research Manager ────► Creates Structured Research Blueprint & Subtopics
      │
      ▼
Agent 2: Web Researcher  ────► Executes Live Searches via Tavily Cloud API
      │
      ▼
Agent 3: Source Analyst  ────► Maps Evidence, Statistics & Claims to Source IDs
      │
      ▼
Agent 4: Fact Checker    ────► Re-searches Questionable Data & Confirms Factual Ground Truth
      │
      ▼
Agent 5: Report Writer   ────► Synthesizes Executive Report with Inline Citations [1], [2]
      │
      ▼
Final Verified Report & Sources Directory (Downloadable as Markdown / Text)
```

---

## 🤖 The 5 Specialized Agents

In CrewAI, an **Agent** is a digital specialist with a specific role, goal, and background story.

| Agent | Name | Everyday Analogy | Responsibility | Has Search Tool? |
|---|---|---|---|---|
| **Agent 1** | **Research Manager** | The Project Director | Analyzes your topic, breaks it down into 3–5 subtopics, determines required source types, and plans the workflow. | ❌ No (Focuses purely on strategic planning) |
| **Agent 2** | **Web Researcher** | The Field Investigator | Runs targeted web queries on Tavily to find authoritative reports, government studies, and reputable articles. | ✅ Yes (`tavily_web_search`) |
| **Agent 3** | **Source Analyst** | The Evidence Analyst | Sifts through retrieved search results, extracts key statistics, removes spam/duplicates, and tags every fact to its Source ID. | ❌ No (Focuses on critical evaluation) |
| **Agent 4** | **Fact Checker** | The Senior Editor | Cross-examines extracted claims. If a metric looks suspicious or conflicting, re-searches the web with Tavily to confirm the truth. | ✅ Yes (`tavily_web_search`) |
| **Agent 5** | **Report Writer** | The Publication Author | Writes the final polished research report using ONLY the verified facts. Adds inline citations `[1]`, `[2]` and lists all genuine URLs at the end. | ❌ No (Writes strictly from verified evidence) |

---

## 🛠️ Tools & Cloud Architecture

### What is a "Tool"?
A **Tool** is an external skill or service given to an agent. 

* In this project, the only external tool used is **`TavilySearchTool`** in [`tools/tavily_search_tool.py`](file:///e:/Research%20piolot%20multiagent/tools/tavily_search_tool.py).
* **100% Cloud-Based**: The research runs exclusively over remote HTTPS APIs. 
* **Zero Local OS Dependencies**: No local Chrome browser, no ChromeDriver, no Selenium, no Playwright, and no local databases are required. This ensures it deploys seamlessly to **Streamlit Community Cloud**.

---

## 📌 How Citations and Sources Work

A major problem with traditional AI chatbots is **hallucination**—making up quotes, study names, or fake URLs. ResearchPilot AI solves this through a 4-step citation pipeline:

1. **Capture**: When Agent 2 searches Tavily, each result is assigned a unique tracking ID (`[S1]`, `[S2]`) and its URL, page title, domain, and snippet are saved in the [`SourceRegistry`](file:///e:/Research%20piolot%20multiagent/tools/source_utils.py).
2. **Deduplication**: Duplicate URLs and tracking tags (like `?utm_source=...`) are automatically stripped and normalized.
3. **Verification**: The Fact Checker verifies the claims and assigns permanent reference indices `[1]`, `[2]`.
4. **Alignment**: The Report Writer places inline brackets:
   ```markdown
   Generative AI is increasingly deployed in defensive cybersecurity operations [1].
   However, automated spear-phishing techniques present emerging detection challenges [2][3].
   ```
   At the end of the report, the system renders the verified bibliography:
   ```markdown
   ### Sources
   [1] CISA Releases AI Security Guidance — cisa.gov
   https://www.cisa.gov/resources-tools/resources/guidelines-secure-ai-system-development

   [2] NIST AI Risk Management Framework — nist.gov
   https://www.nist.gov/itl/ai-risk-management-framework
   ```

---

## 📁 Project Directory Structure

```
researchpilot-ai/
├── app.py                      # Streamlit User Interface & interaction logic
├── api.py                      # Centralized Groq LLM setup & secret reader
├── crew.py                     # CrewAI orchestration (wires agents and tasks)
├── smoke_test.py               # Automated verification test script
├── requirements.txt            # Pinned dependencies for Python 3.12
├── README.md                   # Beginner guide and documentation
├── DEPLOYMENT.md               # GitHub to Streamlit Cloud deployment guide
├── .gitignore                  # Keeps secrets and temporary files out of Git
│
├── agents/                     # Who performs the work (1 file per agent)
│   ├── __init__.py
│   ├── manager_agent.py        # Agent 1: Research Manager
│   ├── researcher_agent.py     # Agent 2: Web Researcher
│   ├── source_analyst_agent.py # Agent 3: Source Analyst
│   ├── fact_checker_agent.py   # Agent 4: Fact Checker
│   └── report_writer_agent.py  # Agent 5: Report Writer
│
├── tasks/                      # What work must be performed (1 file per task)
│   ├── __init__.py
│   ├── research_plan_task.py   # Task 1: Research planning
│   ├── research_task.py        # Task 2: Live web research execution
│   ├── analysis_task.py        # Task 3: Evidence analysis & mapping
│   ├── fact_check_task.py      # Task 4: Fact-checking & corroboration
│   └── report_task.py          # Task 5: Final cited report generation
│
├── tools/                      # External capabilities & citation utilities
│   ├── __init__.py
│   ├── tavily_search_tool.py   # Tavily web search tool (BaseTool)
│   ├── source_utils.py         # URL normalization & SourceRegistry
│   └── citation_utils.py       # Inline citation parser & bibliography builder
│
├── config/                     # Prompts and configurations (YAML)
│   ├── agents.yaml             # Agent roles, goals, and backstories
│   └── tasks.yaml              # Task descriptions and expected outputs
│
└── .streamlit/                 # Streamlit configuration
    ├── config.toml             # Theme and server settings
    └── secrets.toml.example    # Secrets template (Never commit secrets.toml!)
```

---

## 🔑 Getting Your API Keys

You need two free API keys to run this application:

### 1. Groq API Key (Powers the Fast LLM)
1. Visit [Groq Console](https://console.groq.com/).
2. Create a free account or sign in with Google/GitHub.
3. Click **API Keys** in the left menu.
4. Click **Create API Key**, copy your key (starts with `gsk_...`), and save it securely.

### 2. Tavily API Key (Powers the Live Web Search)
1. Visit [Tavily](https://app.tavily.com/).
2. Sign up for a free account.
3. On your dashboard, copy your API Key (starts with `tvly-...`).

---

## 💻 Local Quickstart

### 1. Prerequisites
* **Python 3.12** installed on your computer.

### 2. Clone or Download This Repository
```bash
git clone https://github.com/your-username/researchpilot-ai.git
cd researchpilot-ai
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Secrets
Copy the example secrets file:
```bash
# On Windows PowerShell:
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml

# On Linux/macOS:
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Open `.streamlit/secrets.toml` in your text editor and insert your actual keys:
```toml
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
TAVILY_API_KEY = "tvly-your_actual_tavily_api_key_here"
GROQ_MODEL = "openai/gpt-oss-120b"
```

### 5. Run the Smoke Test
```bash
python smoke_test.py
```

### 6. Start the Streamlit Web Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser!

---

## 🐍 Why Python 3.12?

CrewAI officially requires **Python >= 3.10 and < 3.14**. 
* **Python 3.14** is too new; many AI and C-extension dependencies (such as Pydantic Core and ChromaDB) do not yet offer pre-built binary wheels for 3.14.
* **Python 3.12** is the modern, stable standard supported by PyPI, CrewAI, and Streamlit Community Cloud.

---

## ☁️ Deploying to Streamlit Community Cloud

See the step-by-step guide in [DEPLOYMENT.md](file:///e:/Research%20piolot%20multiagent/DEPLOYMENT.md) for full instructions:
1. Push your repository to GitHub.
2. Log into [share.streamlit.io](https://share.streamlit.io).
3. Connect your repository, select `app.py`, and choose Python 3.12.
4. Paste your `GROQ_API_KEY` and `TAVILY_API_KEY` in the **Advanced Settings -> Secrets** box.
5. Click **Deploy**!

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| **"Missing required credentials"** | `GROQ_API_KEY` or `TAVILY_API_KEY` is not detected. | Check that `.streamlit/secrets.toml` exists locally or that keys are saved in Streamlit Cloud Secrets. |
| **"Rate limit reached on Groq"** | Groq's per-minute token budget is exceeded. | ResearchPilot caps prompts at 2,500 bytes and completions at 768 tokens, limits retrieved snippets, and avoids duplicate task context. If the account's rolling limit is still exhausted, wait and retry or choose "Quick" research depth. |
| **"Tavily search returned 0 results"** | The query is too narrow or uses uncommon syntax. | Rephrase your research topic using broader, standard keywords. |
| **No citations visible** | Sources section was omitted by LLM output. | ResearchPilot's `citation_utils.py` will automatically append the verified sources directory at the bottom. |

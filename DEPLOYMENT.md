# 🚀 Streamlit Community Cloud Deployment Guide

A step-by-step, beginner-friendly guide to taking **ResearchPilot AI** from your local computer to the cloud via GitHub and Streamlit Community Cloud.

---

## 📋 The Complete Workflow at a Glance

```
1. Get Groq Key ──► 2. Get Tavily Key ──► 3. Create GitHub Repo ──► 4. Push Code ──► 5. Deploy on Streamlit Cloud
```

---

## Step 1: Create Your Free Groq API Key

1. Go to the [Groq Console](https://console.groq.com/).
2. Sign in with your Google, GitHub, or email account.
3. In the left navigation sidebar, click on **API Keys**.
4. Click **Create API Key**.
5. Give it a name (e.g., `ResearchPilot-Groq`).
6. Copy the key (it starts with `gsk_...`) and store it somewhere safe temporarily (like a private notepad). You will need it in Step 6.

---

## Step 2: Create Your Free Tavily API Key

1. Go to [Tavily Search](https://app.tavily.com/).
2. Sign up for a free account.
3. On your user dashboard, locate your **API Key** (it starts with `tvly-...`).
4. Copy and store it alongside your Groq key.

---

## Step 3: Create a New GitHub Repository

1. Open your browser and go to [GitHub](https://github.com/).
2. Log in and click the **+** (plus) icon in the top-right corner, then select **New repository**.
3. Fill in the repository details:
   - **Repository name:** `researchpilot-ai`
   - **Description:** `Autonomous Multi-Agent Research Assistant powered by Groq, CrewAI, and Tavily`
   - **Public or Private:** You can choose either (Streamlit Community Cloud works with both).
   - **Initialize this repository with:** Leave checkboxes unchecked (do not add a README or .gitignore on GitHub since we already have them locally).
4. Click **Create repository**.

---

## Step 4: Verify `.gitignore` and Security Checks

> [!CAUTION]
> **NEVER COMMIT SECRETS OR REAL API KEYS TO GITHUB!**
> Anyone with access to your repository can steal your API keys if you commit them.

Check your project folder to ensure `.gitignore` exists and contains:
```gitignore
.streamlit/secrets.toml
.env
```
Ensure you have **NOT** renamed `.streamlit/secrets.toml.example` directly into git staging. Only use `.streamlit/secrets.toml` locally, and let `.gitignore` hide it.

---

## Step 5: Upload Project to GitHub

Open your terminal or PowerShell in your project folder (`e:\Research piolot multiagent`):

```bash
# Initialize git if not already initialized
git init

# Check the status to ensure secrets.toml is NOT listed
git status

# Add all project files
git add .

# Create initial commit
git commit -m "Initial commit of ResearchPilot AI multi-agent application"

# Rename branch to main
git branch -M main

# Link to your GitHub repository (replace with your actual GitHub URL)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/researchpilot-ai.git

# Push code to GitHub
git push -u origin main
```

Now, refresh your GitHub repository page in your browser. You should see all the files (`app.py`, `api.py`, `crew.py`, `agents/`, `tasks/`, `tools/`, `config/`, `requirements.txt`, etc.).

---

## Step 6: Deploy on Streamlit Community Cloud

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **Sign in** (use **Continue with GitHub** to automatically link your repositories).
3. Once logged in to your workspace, click the **Create app** (or **New app**) button.
4. Select **I already have an app**.
5. Configure your app deployment settings:
   - **Repository:** Select `YOUR_GITHUB_USERNAME/researchpilot-ai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** (Optional custom subdomain, or leave default)
6. Click **Advanced settings** (at the bottom of the form):
   - **Python version:** Select **`3.12`**. (Do not select 3.14).
   - In the **Secrets** text box, paste your API keys in TOML format:
     ```toml
     GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
     TAVILY_API_KEY = "tvly-your_actual_tavily_api_key_here"
     GROQ_MODEL = "openai/gpt-oss-120b"
     ```
7. Click **Save** in the Advanced Settings dialog.
8. Click **Deploy!**

---

## Step 7: Monitor Build and Launch

1. Streamlit Community Cloud will start preparing the virtual environment.
2. It will automatically detect `requirements.txt` and install:
   - `crewai==1.15.23`
   - `crewai-tools==1.15.23`
   - `groq==1.7.0`
   - `streamlit==1.64.0`
   - `tavily-python==0.8.4`
3. Within 2–3 minutes, the console log will show the app starting, and your live web interface will appear with the title **🧭 ResearchPilot AI**.

---

## Step 8: Test the Research Workflow

1. In the sidebar, verify that both badges show:
   - `✅ Groq Active`
   - `✅ Tavily Active`
2. Select your **Research Depth** (start with `Standard` or `Quick`).
3. Click one of the example topic buttons, such as:
   - `Impact of Generative AI on Cybersecurity Defense and Phishing in 2026`
4. Click **🚀 Start Multi-Agent Research**.
5. Watch the real-time status box as each of the 5 agents executes:
   - Manager plans the subtopics.
   - Researcher queries Tavily.
   - Analyst maps claims to source IDs.
   - Fact Checker corroborates numbers.
   - Writer authors the cited publication.
6. Verify the final output:
   - Confirm that the report text contains inline citations like `[1]`, `[2]`.
   - Confirm that the bottom section lists all authentic sources with active URLs.
   - Click the **🌐 Verified Sources** tab to expand details on the retrieved pages.
   - Use the **💾 Export & Download** tab to download your report as a `.md` or `.txt` file.

Congratulations! Your multi-agent AI research assistant is now live in production on the cloud!

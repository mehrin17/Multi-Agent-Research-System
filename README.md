# Multi-Agent Research System

**Discover → Extract → Synthesize → Review**

A basic Streamlit research assistant that searches the web with Tavily, extracts accessible pages with Requests and BeautifulSoup, drafts a report with a Groq chat model through LangChain, asks a separate critic call to review the draft, and attempts a separate revision call. It displays source URLs and lets users download the report.

## Managed hosting

The managed website runs the same Streamlit app in a Python container. A small Nginx reverse proxy forwards the app and WebSocket traffic and serves `manus-routes.json` at the site root. Groq and Tavily credentials are supplied at runtime through the host's protected environment and must not be committed to source files.

## Requirements

- Python 3.10 or newer
- A [Groq API key](https://console.groq.com/keys)
- A [Tavily API key](https://app.tavily.com/)

## Windows PowerShell setup

From the project folder, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Add your API keys to `.env` (never commit that file):

```dotenv
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Save `.env`, then launch:

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`). If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current terminal and activate again.

## Workflow components

- **Search (`tools.py`)** — Calls Tavily and returns real result titles, URLs, and snippets.
- **Reader (`tools.py`)** — Fetches webpages, removes common non-content elements, and extracts text. Failures are recorded while other sources continue.
- **Writer (`agents.py`)** — Uses a Groq chat model via `langchain-groq` to write an evidence-based report with source labels.
- **Critic (`agents.py`)** — Makes an independent LLM call to evaluate clarity, relevance, missing information, and support.
- **Revision (`agents.py`)** — Makes a further call to apply the critique when possible; if revision fails, the draft and critique remain available.
- **Pipeline (`pipeline.py`)** — Orchestrates these stages and preserves source URLs.
- **Frontend (`app.py`)** — Shows progress, report, critique, source links, and a Markdown download.

If page extraction fails, the search snippet is still available to the writer and the source is clearly identified. If Tavily has no usable results or an essential API key is missing, the interface shows an error rather than inventing search results. As with any LLM-generated synthesis, verify important claims against the linked primary sources.

## Project files

```text
app.py
agents.py
tools.py
pipeline.py
requirements.txt
.env.example
.gitignore
README.md
Dockerfile
start.sh
nginx.conf.template
manus-routes.json
app.config.ts
```

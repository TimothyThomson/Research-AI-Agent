# ResearchMind

ResearchMind is a multi-agent AI research system built with LangChain and Streamlit. It searches the web, scrapes relevant sources, drafts a structured research report, and then critiques the final output.

## Features

- Search agent for recent web information
- Reader agent for scraping deeper page content
- Writer chain for generating a polished report
- Critic chain for scoring and improving the report
- Streamlit UI for running the full pipeline in the browser
- CLI pipeline for terminal-based research runs

## Project Structure

```text
.
├── app.py              # Streamlit web app
├── pipeline.py         # Command-line research pipeline
├── agents.py           # LangChain agents and writing/critic chains
├── tools.py            # Web search and scraping tools
├── requirements.txt    # Python dependencies
└── .env                # Local API keys, not for sharing
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If Streamlit is not included in your environment, install it:

```bash
pip install streamlit
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Do not commit or share real API keys. If a key is exposed, revoke it and create a new one.

## Run the Web App

```bash
streamlit run app.py
```

If you are using the project virtual environment directly:

```bash
.venv/bin/streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Run from Terminal

```bash
python pipeline.py
```

Enter a research topic when prompted.

## How It Works

1. The search agent uses Tavily to gather recent and relevant results.
2. The reader agent selects a useful URL and scrapes page text.
3. The writer chain combines the search results and scraped content into a report.
4. The critic chain reviews the report and provides feedback.

## Troubleshooting

If you see an API key error, check that `.env` is saved in the project root and contains real keys, not placeholder values.

If VS Code shows missing imports, make sure it is using the same Python interpreter where dependencies were installed:

```text
Python: Select Interpreter -> .venv/bin/python
```

If the UI still shows an old error after editing `.env`, fully restart Streamlit with `Ctrl + C`, then run it again.

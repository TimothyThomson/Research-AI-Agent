from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from pathlib import Path
from rich import print

ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(ENV_PATH, override=True)


def get_env_status(name: str) -> str:
    value = os.getenv(name, "").strip().strip("\"'")
    if value.startswith("replace_with"):
        return "placeholder value still present"
    if value:
        return "present"
    if not ENV_PATH.exists():
        return "missing"
    if ENV_PATH.stat().st_size == 0:
        return "empty"
    return f"present but {name} was not found"


def get_tavily_client() -> TavilyClient | None:
    api_key = os.getenv("TAVILY_API_KEY")
    if get_env_status("TAVILY_API_KEY") != "present":
        return None
    return TavilyClient(api_key=api_key)

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    tavily = get_tavily_client()
    if tavily is None:
        return (
            "TAVILY_API_KEY is not set to a real key. Replace the placeholder "
            f"value in {ENV_PATH} with your actual Tavily API key. "
            f"Current .env status: {get_env_status('TAVILY_API_KEY')}."
        )

    try:
        results = tavily.search(query=query,max_results=5)
    except Exception as e:
        return f"Web search failed: {str(e)}"

    out = []

    for r in results.get('results', []):
        out.append(
            f"Title: {r.get('title', 'Untitled')}\n"
            f"URL: {r.get('url', 'No URL')}\n"
            f"Snippet: {r.get('content', '')[:300]}\n"
        )

    if not out:
        return "No search results found."

    return "\n----\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

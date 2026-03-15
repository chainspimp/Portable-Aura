"""
web_search.py — AURA Portable Edition
Simple DuckDuckGo search, no API key needed.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def search(query: str, max_results: int = 4) -> List[Dict]:
    """
    Search DuckDuckGo. Returns list of {title, url, snippet}.
    Falls back gracefully if duckduckgo_search is not installed.
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title":   r.get("title", ""),
                    "url":     r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
        return results
    except ImportError:
        logger.warning("duckduckgo_search not installed.")
        return [{"title": "Search unavailable", "url": "", "snippet": "Install duckduckgo-search package."}]
    except Exception as e:
        logger.error(f"Search error: {e}")
        return [{"title": "Search failed", "url": "", "snippet": str(e)}]


def format_for_context(results: List[Dict]) -> str:
    """Format search results into a compact string for LLM context."""
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}\n    {r['snippet']}\n    {r['url']}")
    return "\n\n".join(lines)


def should_search(text: str) -> bool:
    """Quick heuristic — does this message likely need a web search?"""
    triggers = [
        "search", "look up", "find", "what is", "who is", "when did",
        "latest", "news", "current", "today", "price of", "weather",
        "how many", "where is", "definition of", "tell me about",
    ]
    lower = text.lower()
    return any(t in lower for t in triggers)

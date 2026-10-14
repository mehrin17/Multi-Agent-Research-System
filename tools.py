"""Web search and page extraction utilities for the research workflow."""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

TAVILY_ENDPOINT = "https://api.tavily.com/search"


def search_web(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Search Tavily and normalize results; raises useful errors on failures."""
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is missing. Add it to your .env file.")
    try:
        response = requests.post(
            TAVILY_ENDPOINT,
            json={"api_key": api_key, "query": query, "search_depth": "basic", "max_results": max_results, "include_answer": False},
            timeout=30,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Web search failed: {exc}") from exc
    results = []
    for item in payload.get("results", []):
        url = str(item.get("url", "")).strip()
        if not url or urlparse(url).scheme not in {"http", "https"}:
            continue
        results.append({"title": str(item.get("title") or url), "url": url, "snippet": str(item.get("content") or "")})
    if not results:
        raise RuntimeError("Tavily returned no usable search results. Try a more specific question.")
    return results


def extract_page(url: str, timeout: int = 15, max_chars: int = 12000) -> str:
    """Extract readable text from an HTTP webpage using BeautifulSoup."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchPrototype/1.0)"}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for node in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
        node.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = " ".join(main.get_text(" ", strip=True).split())
    if len(text) < 100:
        raise ValueError("Page contained too little readable text.")
    return text[:max_chars]


def read_sources(results: list[dict[str, str]]) -> list[dict[str, str]]:
    """Read all possible pages, retaining every search result and its URL."""
    sources = []
    for result in results:
        source = {**result, "text": "", "read_error": ""}
        try:
            source["text"] = extract_page(result["url"])
        except (requests.RequestException, ValueError, RuntimeError) as exc:
            source["read_error"] = str(exc)
        sources.append(source)
    return sources

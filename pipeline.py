"""Orchestration for the Discover → Extract → Synthesize → Review workflow."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agents import critique_report, revise_report, write_report
from tools import read_sources, search_web

ProgressCallback = Callable[[str], None]


def _evidence_block(sources: list[dict[str, str]]) -> str:
    blocks = []
    for index, source in enumerate(sources, start=1):
        body = source["text"] or source["snippet"] or "No readable page text or search snippet was available."
        status = "" if source["text"] else f" (page extraction failed: {source['read_error'] or 'using search snippet only'})"
        blocks.append(f"[S{index}] {source['title']} — {source['url']}{status}\n{body}")
    return "\n\n".join(blocks)


def run_research(question: str, progress: ProgressCallback | None = None, max_results: int = 5) -> dict[str, Any]:
    """Run all distinct research stages and return report, critique, and sources."""
    question = question.strip()
    if not question:
        raise ValueError("Enter a research question before starting.")
    notify = progress or (lambda _message: None)
    notify("Discovering relevant webpages with Tavily…")
    results = search_web(question, max_results=max_results)
    notify(f"Found {len(results)} results. Extracting accessible webpage content…")
    sources = read_sources(results)
    readable_count = sum(bool(source["text"]) for source in sources)
    notify(f"Extracted readable text from {readable_count} of {len(sources)} pages. Synthesizing the report…")
    evidence = _evidence_block(sources)
    draft = write_report(question, evidence)
    notify("Reviewing the draft for gaps, clarity, relevance, and unsupported claims…")
    try:
        critique = critique_report(question, draft, evidence)
    except RuntimeError:
        critique = "Critique unavailable: the independent critic call failed."
        final_report = draft + "\n\n> Review note: This draft was not independently reviewed because the critic call failed."
    else:
        notify("Applying the review and preparing the final report…")
        try:
            final_report = revise_report(question, draft, critique, evidence)
        except RuntimeError:
            # Keep a usable draft and clearly disclose that the optional revision call failed.
            final_report = draft + "\n\n> Revision note: The critique was generated, but the final revision call failed. See the critique below."
    notify("Research complete.")
    return {"question": question, "report": final_report, "draft": draft, "critique": critique, "sources": sources, "readable_count": readable_count}

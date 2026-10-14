"""Writer and critic agents. Each stage makes its own Groq chat-model call."""
from __future__ import annotations

import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Groq retired llama-3.3-70b-versatile for developer/free-tier use in 2026.
DEFAULT_MODEL = "openai/gpt-oss-120b"


def _model() -> ChatGroq:
    if not os.getenv("GROQ_API_KEY", "").strip():
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    model_name = os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    try:
        return ChatGroq(model=model_name, temperature=0.2, max_retries=2, timeout=60)
    except Exception as exc:
        raise RuntimeError(f"Could not initialize Groq model '{model_name}': {exc}") from exc


def _invoke(prompt: ChatPromptTemplate, **values: str) -> str:
    try:
        result = (prompt | _model()).invoke(values)
        content = result.content
        if isinstance(content, str):
            return content.strip()
        return "\n".join(str(part) for part in content).strip()
    except Exception as exc:
        raise RuntimeError(f"Groq request failed: {exc}") from exc


def write_report(question: str, evidence: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("human", "You are a careful research writer. Use only the supplied evidence. Never invent facts, citations, or sources. Distinguish evidence from uncertainty. Cite claims inline using [S1], [S2], etc. Produce a concise, structured report with a title, Executive Summary, Findings, Limitations, and Conclusion.\n\nResearch question: {question}\n\nEvidence and source labels:\n{evidence}\n\nWrite the report. If evidence is insufficient, say so explicitly."),
    ])
    return _invoke(prompt, question=question, evidence=evidence)


def critique_report(question: str, report: str, evidence: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("human", "You are an independent research critic. Assess relevance, clarity, missing information, and whether factual claims are supported by the provided evidence. Do not add facts. Return a concise critique with actionable corrections; explicitly say when you find no material issues.\n\nQuestion: {question}\n\nDraft report:\n{report}\n\nAvailable evidence:\n{evidence}\n\nCritique the draft."),
    ])
    return _invoke(prompt, question=question, report=report, evidence=evidence)


def revise_report(question: str, report: str, critique: str, evidence: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("human", "Revise a research report in response to the critique. Use only the supplied evidence, retain citations [S1] etc., remove or qualify unsupported statements, and be transparent about gaps. Do not invent sources. Keep a clear structure.\n\nQuestion: {question}\n\nDraft:\n{report}\n\nCritique:\n{critique}\n\nEvidence:\n{evidence}\n\nReturn the improved final report."),
    ])
    return _invoke(prompt, question=question, report=report, critique=critique, evidence=evidence)

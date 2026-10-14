"""Streamlit frontend for the Multi-Agent Research System."""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from pipeline import run_research

load_dotenv()

st.set_page_config(page_title="Multi-Agent Research System", page_icon="🔎", layout="wide")
st.title("Multi-Agent Research System")
st.caption("Discover → Extract → Synthesize → Review")
st.markdown("Ask a research question. Separate search, reader, writer, and critic stages gather and review web evidence before presenting a sourced report.")

with st.sidebar:
    st.subheader("Configuration")
    if os.getenv("TAVILY_API_KEY") and os.getenv("GROQ_API_KEY"):
        st.success("API keys detected")
    else:
        st.warning("Add GROQ_API_KEY and TAVILY_API_KEY to the project environment (or local .env file), then restart the app.")
    st.caption(f"Groq model: {os.getenv('GROQ_MODEL') or 'openai/gpt-oss-120b (default)'}")

with st.form("research_form"):
    question = st.text_area("Research question", placeholder="e.g., What are the latest evidence-based approaches to reducing urban heat?", height=110)
    submitted = st.form_submit_button("Start Research", type="primary", use_container_width=True)

if submitted:
    if not question.strip():
        st.error("Please enter a research question.")
    elif not os.getenv("GROQ_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        st.error("Required API key(s) are missing. Add them to the project environment (or local .env file), then restart the app.")
    else:
        status = st.status("Starting research…", expanded=True)
        try:
            result = run_research(question, progress=lambda message: status.write(message))
            status.update(label="Research complete", state="complete", expanded=False)
            st.subheader("Final Research Report")
            st.markdown(result["report"])
            report_text = f"# Research report\n\nQuestion: {result['question']}\n\n{result['report']}\n\n## Critique summary\n\n{result['critique']}\n"
            st.download_button("Download report (.md)", data=report_text, file_name="research_report.md", mime="text/markdown")
            with st.expander("Critique summary", expanded=False):
                st.markdown(result["critique"])
            with st.expander(f"Sources ({len(result['sources'])})", expanded=False):
                st.caption(f"Readable content extracted from {result['readable_count']} of {len(result['sources'])} pages. Search snippets are used where page extraction fails.")
                for index, source in enumerate(result["sources"], start=1):
                    st.markdown(f"**[S{index}] [{source['title']}]({source['url']})**")
                    if source["snippet"]:
                        st.write(source["snippet"])
                    if source["read_error"]:
                        st.caption(f"Page extraction unavailable; snippet retained. ({source['read_error']})")
        except Exception as exc:
            status.update(label="Research stopped", state="error", expanded=True)
            st.error(f"Research could not be completed: {exc}")
            st.info("Check your API keys and network connection, then try again. Page extraction failures alone do not stop the workflow.")

st.divider()
st.caption("Prototype note: findings are generated from retrieved web evidence and should be independently verified for high-stakes use.")

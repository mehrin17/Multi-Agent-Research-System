# Project outcomes

## 1. Research interface and result presentation
- The frontend includes the project title and short description, research question input, Start Research button, progress messages for each stage, final research report, expandable source links, critique summary, download report button, and clear error messages.
- Display the final report and source links; preserve the original source URLs.
- Show a critique summary and provide a report download.

## 2. Search and webpage extraction
- The Search Agent uses Tavily to search the web for the user's research question and returns relevant titles, URLs, and snippets.
- The Reader Agent uses requests and BeautifulSoup to extract readable text from accessible webpages. Preserve the source URLs. If scraping fails, continue with the other sources.
- Do not invent sources or fabricate search results. Explain when evidence is limited.

## 3. Report writing, independent review, and finalization
- The Writer Chain uses a Groq chat model through LangChain to generate a structured research report using collected information.
- The Critic Chain makes a separate LLM call to review the report for missing information, clarity, unsupported claims, and relevance.
- Use the critique to improve the draft when possible. Display the final report and source links.

## 4. Configuration and reliability
- Load credentials using python-dotenv. Provide configuration for GROQ_API_KEY, TAVILY_API_KEY, and GROQ_MODEL; never hard-code API keys.
- Handle missing API keys, failed searches, scraping errors, and LLM failures gracefully.
- Keep search, reader, writer, and critic as separate components.

## 5. Permanent hosted website
- Make the working Python/Streamlit prototype available at a stable, publicly accessible website URL rather than only the temporary Sandbox preview.
- Preserve the requested technology stack and simple project scope; do not add a database, authentication, React, or unnecessary frameworks.
- Verify the published website responds successfully before marking this outcome complete.

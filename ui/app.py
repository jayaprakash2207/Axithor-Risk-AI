import json
import os
import re
import sys
import tempfile
from typing import Dict, List, Optional, Tuple

import streamlit as st

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from analysis.comparison_engine import compare_reports
from analysis.risk_analyzer import RiskAnalyzer
from llm.gemini_interface import GeminiClient
from parser.html_parser import SEC10KHtmlParser
from parser.pdf_parser import PDFParser
from retrieval.rule_engine import RuleBasedRetriever
from segmentation.section_splitter import SectionSplitter


st.set_page_config(page_title="Axithor Risk AI", layout="wide")

st.title("Axithor Risk AI")
st.caption("Explainable vectorless RAG for SEC filings, risk discovery, and report comparison.")

use_ollama = st.checkbox("Use LLM (Gemini)", value=True, disabled=True)
model_name = st.text_input("Gemini model", value="gemini-2.5-flash")
api_key_value = st.text_input(
    "Gemini API key",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Paste your Gemini API key here or set GEMINI_API_KEY before launching Streamlit.",
)
if not api_key_value:
    st.warning("Gemini API key is not set. Paste it above or set GEMINI_API_KEY before running analysis.")

def _parse_upload(
    uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    parser = PDFParser(extract_tables=False)
    html_parser = SEC10KHtmlParser()
    splitter = SectionSplitter()

    file_name = uploaded_file.name.lower()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_name) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        if file_name.endswith(".pdf"):
            parsed = parser.parse(tmp_path)
            cleaned_text = parsed.text
        elif file_name.endswith(".html") or file_name.endswith(".htm"):
            cleaned_text = html_parser.parse(tmp_path)
        else:
            st.error(f"Unsupported file type: {uploaded_file.name}")
            return None, None

        sections = splitter.split(cleaned_text)
        return sections, cleaned_text
    except Exception as exc:
        st.error(f"Failed to parse {uploaded_file.name}: {exc}")
        return None, None


def _extract_year(name: str) -> Optional[int]:
    match = re.search(r"(19|20)\d{2}", name)
    if not match:
        return None
    return int(match.group(0))


def _build_report_payload(name: str, sections: Dict[str, str]) -> Dict[str, str]:
    return {
        "company": name,
        "year": _extract_year(name),
        "risk_factors": sections.get("risk_factors", ""),
        "mda": sections.get("mda", ""),
        "notes": sections.get("notes", ""),
        "legal": sections.get("legal", ""),
        "auditor_notes": sections.get("auditor_notes", ""),
    }


def _missing_section_warnings(sections: Dict[str, str]) -> None:
    if not sections.get("risk_factors"):
        st.warning("Risk factors section missing or empty.")
    if not sections.get("mda"):
        st.warning("MD&A section missing or empty.")


def _json_download_button(data: Dict[str, object], label: str) -> None:
    st.download_button(
        label=label,
        data=json.dumps(data, indent=2),
        file_name="risk_analysis.json",
        mime="application/json",
    )


def _section_stats(sections: Dict[str, str]) -> List[Dict[str, object]]:
    stats: List[Dict[str, object]] = []
    total_chars = sum(len(text) for text in sections.values() if text)
    for name, text in sections.items():
        if not text:
            continue
        char_count = len(text)
        share = round((char_count / total_chars) * 100, 1) if total_chars else 0.0
        stats.append(
            {
                "section": name,
                "chars": char_count,
                "share": share,
                "preview": text[:220],
            }
        )
    return stats


def _render_vectorless_rag_view(
    cleaned_text: str,
    sections: Dict[str, str],
    retrieved: List[object],
    query: str,
) -> None:
    st.markdown("### Vectorless RAG View")
    st.info(
        "This project does not store embeddings or vectors. It keeps cleaned text in memory, "
        "splits it into named sections, then ranks those sections with rules based on your query."
    )

    total_chars = len(cleaned_text)
    section_count = len([name for name, text in sections.items() if text])
    retrieved_count = len(retrieved)
    top_context_chars = sum(len(item.text) for item in retrieved)

    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    with metric_a:
        st.metric("Raw Text Chars", total_chars)
    with metric_b:
        st.metric("Stored Sections", section_count)
    with metric_c:
        st.metric("Retrieved Sections", retrieved_count)
    with metric_d:
        st.metric("Context Chars Sent", top_context_chars)

    st.markdown("#### Pipeline")
    pipe_a, pipe_b, pipe_c, pipe_d = st.columns(4)
    with pipe_a:
        st.markdown("**1. Parse**")
        st.caption("PDF/HTML to cleaned plain text")
        st.code(cleaned_text[:350] or "No text", language="text")
    with pipe_b:
        st.markdown("**2. Store**")
        st.caption("Named in-memory section buckets")
        st.json({name: len(text) for name, text in sections.items() if text})
    with pipe_c:
        st.markdown("**3. Retrieve**")
        st.caption(f"Rule match for query: {query}")
        st.json(
            [
                {"section": item.section, "score": round(item.score, 3), "chars": len(item.text)}
                for item in retrieved
            ]
        )
    with pipe_d:
        st.markdown("**4. Analyze**")
        st.caption("Concatenated retrieved text goes to Gemini")
        st.code("\n\n".join(item.text[:180] for item in retrieved) or "No retrieved text", language="text")

    st.markdown("#### Section Breakdown")
    for item in _section_stats(sections):
        st.write(f"`{item['section']}`  {item['chars']} chars  ({item['share']}%)")
        st.progress(min(int(item["share"]), 100))
        with st.expander(f"Preview: {item['section']}"):
            st.code(item["preview"], language="text")

    st.markdown("#### In-Memory Shape")
    st.code(
        json.dumps(
            {
                "cleaned_text": f"<{len(cleaned_text)} chars>",
                "sections": {name: f"<{len(text)} chars>" for name, text in sections.items() if text},
                "retrieved_context": [
                    {"section": item.section, "score": round(item.score, 3), "chars": len(item.text)}
                    for item in retrieved
                ],
            },
            indent=2,
        ),
        language="json",
    )


tab_single, tab_compare = st.tabs(["Single Report Analysis", "Compare Reports"])

with tab_single:
    st.subheader("Single Report Analysis")
    uploaded_file = st.file_uploader("Upload a report (PDF or HTML)", type=["pdf", "html", "htm"], key="single")
    query = st.text_input("Ask a question about risks", value="What are the main risks?", key="single_query")
    analyze = st.button("Analyze Report", key="analyze")

    if analyze:
        if not uploaded_file:
            st.warning("Please upload a report before running analysis.")
        else:
            with st.spinner("Analyzing report..."):
                sections, cleaned_text = _parse_upload(uploaded_file)
                if sections and cleaned_text:
                    _missing_section_warnings(sections)

                    retriever = RuleBasedRetriever()
                    llm_client = GeminiClient(model=model_name, api_key=api_key_value)
                    analyzer = RiskAnalyzer(llm_client=llm_client, require_llm=True)

                    retrieved = retriever.retrieve(query, sections, max_sections=2)
                    combined_text = "\n\n".join(result.text for result in retrieved)
                    analysis = analyzer.analyze(combined_text)

                    metric_col, score_col = st.columns(2)
                    with metric_col:
                        st.metric("Top Risks", len(analysis.top_risks))
                    with score_col:
                        st.metric("Confidence Score", analysis.confidence_score)

                    st.markdown("### Summary")
                    st.success(analysis.summary)

                    st.markdown("### Risk Categories")
                    st.json(analysis.risk_categories)

                    st.markdown("### Red Flags")
                    st.write(analysis.red_flags or ["None detected"])

                    with st.expander("Top Risks"):
                        st.write("\n".join(analysis.top_risks) or "None detected")

                    with st.expander("Highlighted Risky Sentences"):
                        st.write("\n".join(analysis.risky_sentences[:50]) or "None detected")

                    with st.expander("How Vectorless RAG Stores This Report", expanded=True):
                        _render_vectorless_rag_view(cleaned_text, sections, retrieved, query)

                    output = {
                        "top_risks": analysis.top_risks,
                        "risk_categories": analysis.risk_categories,
                        "red_flags": analysis.red_flags,
                        "confidence_score": analysis.confidence_score,
                        "summary": analysis.summary,
                        "risky_sentences": analysis.risky_sentences,
                    }
                    _json_download_button(output, "Download JSON")

with tab_compare:
    st.subheader("Compare Reports")
    demo_mode = st.checkbox("Demo Mode (Apple 10-K)", value=False)
    left, right = st.columns(2)

    with left:
        report_a = st.file_uploader("Report A (older)", type=["pdf", "html", "htm"], key="report_a")

    with right:
        report_b = st.file_uploader("Report B (newer)", type=["pdf", "html", "htm"], key="report_b")

    compare = st.button("Compare Reports", key="compare")

    if compare:
        if not report_a or not report_b:
            st.warning("Please upload both reports before comparing.")
        else:
            with st.spinner("Comparing reports..."):
                sections_a, _ = _parse_upload(report_a)
                sections_b, _ = _parse_upload(report_b)

                if sections_a and sections_b:
                    _missing_section_warnings(sections_a)
                    _missing_section_warnings(sections_b)

                    report_old = _build_report_payload(report_a.name, sections_a)
                    report_new = _build_report_payload(report_b.name, sections_b)
                    result = compare_reports(report_old, report_new)

                    metric_col, score_col = st.columns(2)
                    with metric_col:
                        st.metric("New Risks", len(result.new_risks))
                    with score_col:
                        st.metric("Confidence Score", result.confidence_score)

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("### New Risks")
                        st.write(result.new_risks or ["None detected"])

                        st.markdown("### Risk Intensity Change")
                        st.write(result.risk_intensity_change)

                        st.markdown("### Red Flags Delta")
                        st.write(result.new_red_flags or ["None detected"])

                    with col_b:
                        st.markdown("### Removed Risks")
                        st.write(result.removed_risks or ["None detected"])

                        st.markdown("### Tone Shift")
                        st.write(result.tone_change)

                        st.markdown("### Summary")
                        st.write(result.summary)

                    with st.expander("Highlighted Sentences"):
                        st.markdown("**New risk sentences**")
                        st.write("\n".join(result.highlighted_sentences.get("new", [])) or "None")
                        st.markdown("**Removed risk sentences**")
                        st.write("\n".join(result.highlighted_sentences.get("removed", [])) or "None")

                    output = {
                        "new_risks": result.new_risks,
                        "removed_risks": result.removed_risks,
                        "risk_intensity_change": result.risk_intensity_change,
                        "tone_change": result.tone_change,
                        "new_red_flags": result.new_red_flags,
                        "confidence_score": result.confidence_score,
                        "summary": result.summary,
                    }
                    _json_download_button(output, "Download Comparison JSON")

if demo_mode:
    st.info("Demo Mode is enabled, but no demo files are bundled yet.")


# Axithor Risk AI — Technical & Product Documentation

> **Version:** 1.0  
> **Language:** Python 3.x  
> **Interface:** Streamlit Web App + Command-Line Interface (CLI)  
> **AI Backend:** Google Gemini API  
> **License:** All Rights Reserved — Permission Required  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Business Value](#2-problem-statement--business-value)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Key Design Philosophy: Vectorless RAG](#4-key-design-philosophy-vectorless-rag)
5. [Project Structure](#5-project-structure)
6. [Module-by-Module Technical Reference](#6-module-by-module-technical-reference)
   - 6.1 [Entry Point — `main.py`](#61-entry-point--mainpy)
   - 6.2 [Document Parsing — `parser/`](#62-document-parsing--parser)
   - 6.3 [Section Segmentation — `segmentation/`](#63-section-segmentation--segmentation)
   - 6.4 [Rule-Based Retrieval — `retrieval/`](#64-rule-based-retrieval--retrieval)
   - 6.5 [LLM Interface — `llm/`](#65-llm-interface--llm)
   - 6.6 [Risk Analysis — `analysis/risk_analyzer.py`](#66-risk-analysis--analysisrisk_analyzerpy)
   - 6.7 [Report Comparison — `analysis/comparison_engine.py`](#67-report-comparison--analysiscomparison_enginepy)
   - 6.8 [Streamlit UI — `ui/app.py`](#68-streamlit-ui--uiapppy)
7. [End-to-End Data Flow](#7-end-to-end-data-flow)
8. [Features & Capabilities](#8-features--capabilities)
9. [Technology Stack](#9-technology-stack)
10. [Setup & Installation Guide](#10-setup--installation-guide)
11. [Running the Application](#11-running-the-application)
12. [Testing](#12-testing)
13. [Configuration & Environment Variables](#13-configuration--environment-variables)
14. [Input & Output Specification](#14-input--output-specification)
15. [Security Considerations](#15-security-considerations)
16. [Current Limitations](#16-current-limitations)
17. [Roadmap & Future Enhancements](#17-roadmap--future-enhancements)
18. [Glossary](#18-glossary)

---

## 1. Executive Summary

**Axithor Risk AI** is an explainable, AI-powered financial risk intelligence system designed to analyze SEC-style financial filings (10-K annual reports, PDFs, and HTML documents). It automatically extracts, classifies, and summarizes financial risks — enabling analysts, compliance teams, and decision-makers to quickly understand risk exposure in corporate filings without manually reading hundreds of pages.

The system uses a novel **"Vectorless RAG"** (Retrieval-Augmented Generation) architecture: instead of relying on opaque embedding databases, it uses deterministic, rule-based retrieval that keeps every step of the analysis visible, auditable, and explainable. The retrieved context is then sent to **Google Gemini** to produce structured, AI-generated risk summaries.

The application is delivered as both a **Streamlit web application** (interactive UI) and a **command-line tool** (CLI for automation/scripting).

---

## 2. Problem Statement & Business Value

### The Challenge

Financial professionals must review large volumes of SEC filings and annual reports to identify material risks to a company or investment. These documents can be hundreds of pages long, densely written in legal/financial language, and change subtly between reporting periods — making risk changes easy to miss.

Traditional approaches:
- **Manual review** is slow, labor-intensive, and inconsistent.
- **Standard NLP/embedding pipelines** are opaque: it is hard to explain *why* a passage was retrieved or *how* the AI reached a conclusion.

### The Solution

Axithor Risk AI addresses these challenges by:

| Challenge | Solution |
|---|---|
| Time-consuming manual review | Automated parsing and analysis in seconds |
| Opaque AI decisions | Rule-based retrieval — every step is visible |
| Detecting changes between filings | Built-in report comparison engine |
| Dependency on proprietary vector databases | Zero vector store — works fully in memory |
| Identifying critical warning signs | Automated red flag detection (e.g., "going concern") |

### Business Value

- **Risk Teams:** Quickly triage a large portfolio of filings to find high-risk documents.
- **Compliance Officers:** Detect material weaknesses, going-concern notices, and restatements automatically.
- **Investment Analysts:** Compare annual reports year-over-year to spot tone changes and new risk disclosures.
- **Audit Teams:** Use the explainable retrieval trace to verify exactly what text was analyzed.
- **Developers & Researchers:** A clean, modular codebase that is easy to extend with additional parsers, retrieval strategies, or LLM backends.

---

## 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AXITHOR RISK AI                                 │
│                                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐               │
│  │  Input   │    │   Parsing    │    │  Segmentation    │               │
│  │  Layer   │───▶│  Layer       │───▶│  Layer           │               │
│  │          │    │              │    │                  │               │
│  │ PDF/HTML │    │ HTMLParser   │    │ SectionSplitter  │               │
│  │ File     │    │ PDFParser    │    │ (Named Buckets)  │               │
│  └──────────┘    └──────────────┘    └────────┬─────────┘               │
│                                               │                          │
│                                               ▼                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐           │
│  │  Analysis    │    │  LLM Layer   │    │  Retrieval       │           │
│  │  Layer       │◀───│              │◀───│  Layer           │           │
│  │              │    │ GeminiClient │    │                  │           │
│  │ RiskAnalyzer │    │              │    │ RuleBasedRetriever│          │
│  │ Comparison   │    │              │    │                  │           │
│  │ Engine       │    └──────────────┘    └──────────────────┘           │
│  └──────┬───────┘                                                        │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────┐                                                        │
│  │  Output      │                                                        │
│  │  Layer       │                                                        │
│  │              │                                                        │
│  │ Streamlit UI │                                                        │
│  │ CLI / JSON   │                                                        │
│  └──────────────┘                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Component(s) | Responsibility |
|---|---|---|
| **Input** | File system / UI upload | Accepts PDF or HTML files |
| **Parsing** | `html_parser.py`, `pdf_parser.py` | Converts raw documents to clean plain text |
| **Segmentation** | `section_splitter.py` | Splits text into named financial report sections |
| **Retrieval** | `rule_engine.py` | Ranks and selects the most relevant sections for a query |
| **LLM** | `gemini_interface.py` | Sends retrieved context to Gemini AI for analysis |
| **Analysis** | `risk_analyzer.py`, `comparison_engine.py` | Produces structured risk output and report comparisons |
| **Output** | `ui/app.py`, `main.py` | Renders results in Streamlit UI or prints to CLI |

---

## 4. Key Design Philosophy: Vectorless RAG

### What is RAG?

**Retrieval-Augmented Generation (RAG)** is an AI architecture where a large language model (LLM) is given relevant context passages before it generates its output. This improves accuracy and grounds the AI in real document content.

### The Problem with Traditional RAG

Most RAG systems use **vector embeddings** and **vector databases** (e.g., Pinecone, Chroma, FAISS). They:
- Convert text chunks into numerical vectors.
- Store these vectors in a database.
- At query time, compute similarity between the query vector and stored vectors.
- Retrieve the "closest" chunks and send them to the LLM.

While powerful, this approach is:
- **Opaque** — you cannot easily explain *why* a chunk was retrieved.
- **Infrastructure-heavy** — requires a vector database and embedding model.
- **Hard to debug** — similarity scores do not map to human-readable logic.

### Axithor's Vectorless Approach

Instead of vectors, Axithor Risk AI uses **rule-based retrieval**:

1. The parsed document is stored as **clean plain text in memory** — no database.
2. The text is split into **named section buckets** (e.g., `risk_factors`, `mda`, `legal`).
3. When a user submits a query, the system **tokenizes** the query into keywords.
4. A rule engine **scores each section** using:
   - A **base priority score** (some sections like `risk_factors` are inherently more relevant for risk queries).
   - A **keyword match score** (how many query tokens appear in each section).
   - An optional **red-flag bonus** (extra weight if the query contains terms like "restatement" or "default").
5. The **top-scoring sections** are selected and concatenated.
6. This context is sent to **Gemini** for analysis.

### Why This Matters

- Every decision is **traceable** and **explainable**.
- The UI shows the exact retrieval trace: tokens, scores, sections chosen.
- No embedding infrastructure is needed.
- Ideal for **regulatory environments** and **audit use cases** where explainability is mandatory.

---

## 5. Project Structure

```
Axithor-Risk-AI/
│
├── main.py                          # CLI entry point — runs the full pipeline
│
├── analysis/
│   ├── risk_analyzer.py             # Risk extraction, categorization, scoring, LLM integration
│   └── comparison_engine.py         # Year-over-year report comparison logic
│
├── parser/
│   ├── html_parser.py               # SEC 10-K HTML document parser (BeautifulSoup)
│   └── pdf_parser.py                # PDF document parser (pdfplumber + PyMuPDF fallback)
│
├── retrieval/
│   └── rule_engine.py               # Rule-based section retriever & scoring engine
│
├── segmentation/
│   └── section_splitter.py          # Splits cleaned text into named financial sections
│
├── llm/
│   ├── gemini_interface.py          # Google Gemini API client
│   └── ollama_interface.py          # (Legacy) Ollama local LLM interface
│
├── ui/
│   └── app.py                       # Streamlit web application (full interactive UI)
│
├── tests/
│   └── test_section_splitter.py     # Unit tests for section detection
│
├── data/
│   ├── apple_2023.html              # Sample Apple Inc. 10-K annual report (HTML)
│   └── README.txt                   # Notes on sample data
│
├── docs/
│   └── screenshots/                 # UI screenshots and diagrams (SVG)
│
├── requirements.txt                 # Python dependency list
├── README.md                        # Public project readme
├── CONTRIBUTING.md                  # Contribution guidelines
└── LICENSE                          # All rights reserved license
```

---

## 6. Module-by-Module Technical Reference

### 6.1 Entry Point — `main.py`

**Purpose:** Provides a command-line interface (CLI) to run the complete analysis pipeline from the terminal.

**Key Function: `run_pipeline(file_path, query, use_ollama, model)`**

Orchestrates the entire pipeline in sequence:
1. Loads and parses the input file via `_load_text()`.
2. Splits the parsed text into sections using `SectionSplitter`.
3. Retrieves the most relevant sections using `RuleBasedRetriever`.
4. Analyzes the retrieved text using `RiskAnalyzer` (backed by `GeminiClient`).
5. Prints a full JSON output to the terminal.

**CLI Arguments:**

| Argument | Default | Description |
|---|---|---|
| `--file` | `data/apple_2023.html` | Path to a PDF or HTML report file |
| `--query` | `"What are the main risks?"` | The analysis question to ask |
| `--model` | `gemini-2.5-flash` | Gemini model name to use |
| `--use-ollama` | (ignored) | Legacy flag, not functional |

**Example CLI usage:**
```bash
python main.py --file data/apple_2023.html --query "What are the main risks?" --model gemini-2.5-flash
```

---

### 6.2 Document Parsing — `parser/`

#### `parser/html_parser.py` — `SEC10KHtmlParser`

**Purpose:** Parses SEC 10-K filings in HTML format into clean, structured plain text.

**Class: `SEC10KHtmlParser`**

| Method | Description |
|---|---|
| `parse(file_path, return_blocks)` | Main entry. Opens the HTML file, strips noise, extracts text blocks, and returns clean text (or a list of `HtmlBlock` objects). |
| `_strip_noise(soup)` | Removes script, style, nav, header, footer, SVG, hidden (`aria-hidden=true`), and `display:none` elements from the HTML DOM. |
| `_extract_blocks(soup)` | Iterates over heading and paragraph tags. Classifies each as a "heading" (if `<h1>`–`<h6>` or matches `item \d+` pattern) or "paragraph". |
| `_extract_fallback_blocks(soup)` | Used when no structured tags are found. Falls back to line-by-line extraction from raw text. |
| `_blocks_to_text(blocks)` | Converts the block list to plain text. Headings are uppercased. |
| `_normalize_lines(lines)` | Collapses excessive blank lines and trims whitespace. |

**Data class: `HtmlBlock`**
```
HtmlBlock(kind: str, text: str)
  kind: "heading" or "paragraph"
  text: cleaned text content
```

**Parsing Strategy:**
- Uses Python's `BeautifulSoup` with the `html.parser` backend.
- Specifically handles SEC 10-K format where sections are introduced with headings like "ITEM 1A. RISK FACTORS".
- Falls back gracefully to raw text extraction if structured tags are absent.

---

#### `parser/pdf_parser.py` — `PDFParser`

**Purpose:** Parses PDF financial reports into plain text, with dual-library fallback.

**Class: `PDFParser`**

| Method | Description |
|---|---|
| `parse(file_path)` | Opens a PDF, iterates pages, extracts text. Primary library: `pdfplumber`. Falls back to `PyMuPDF (fitz)` on failure. Returns a `ParsedDocument`. |
| `_clean_text(text)` | Normalizes whitespace: collapses multiple spaces/tabs, removes excessive newlines. |

**Data class: `ParsedDocument`**
```
ParsedDocument(
  text: str           # Full cleaned text of entire document
  pages: List[str]    # Per-page text
  tables: Optional[List]  # Extracted tables (when extract_tables=True)
)
```

**Parsing Strategy:**
- Attempts `pdfplumber` first (better for text-heavy financial PDFs).
- On any exception, falls back to `PyMuPDF (fitz)`.
- If both fail, raises `RuntimeError`.
- Optional table extraction (`extract_tables=True`) collects tabular data separately.

---

### 6.3 Section Segmentation — `segmentation/`

#### `segmentation/section_splitter.py` — `SectionSplitter`

**Purpose:** Takes the full cleaned text of a financial report and splits it into named sections that correspond to standard SEC 10-K report items.

**Detected Section Names:**

| Section Key | SEC Equivalent | Detection Patterns |
|---|---|---|
| `risk_factors` | Item 1A | "ITEM 1A", "RISK FACTORS" |
| `mda` | Item 7 | "ITEM 7", "MANAGEMENT'S DISCUSSION AND ANALYSIS" |
| `notes` | Item 8 | "ITEM 8", "NOTES TO FINANCIAL STATEMENTS" |
| `legal` | Item 3 | "ITEM 3", "LEGAL PROCEEDINGS" |
| `auditor_notes` | Auditor Report | "REPORT OF INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM", "INDEPENDENT AUDITOR'S REPORT" |
| `other` | (fallback) | Any text not matching the above; first 5,000 characters used |

**Class: `SectionSplitter`**

| Method | Description |
|---|---|
| `split(text)` | Main entry. Returns a `Dict[str, str]` mapping section names to their text content. |
| `_find_matches(text)` | Scans the document line by line, matching lines against all section patterns using regex. Returns a sorted list of `SectionMatch` objects. |
| `_dedupe_matches(matches)` | Removes duplicate matches (same name and start position). |
| `_build_sections(text, matches)` | Converts match positions into text spans. Each section spans from its detected heading to the next heading. |

**Data class: `SectionMatch`**
```
SectionMatch(name: str, start: int, end: int)
  name:  section key (e.g., "risk_factors")
  start: character offset in text where the section begins
  end:   character offset (updated to next section start during _build_sections)
```

**Fallback Behavior:** If no sections are detected, the first 5,000 characters of the full text are assigned to the `other` bucket, ensuring downstream components always have something to work with.

---

### 6.4 Rule-Based Retrieval — `retrieval/`

#### `retrieval/rule_engine.py` — `RuleBasedRetriever`

**Purpose:** Given a user query and a set of named sections, scores and ranks sections, returning the most relevant ones to forward to the LLM.

**Scoring Formula:**

```
total_score = base_score + keyword_score + red_flag_score

Where:
  base_score     = 1.0 if section is in the priority list, else 0.5
  keyword_score  = (number of query tokens matching section text) / (total query tokens)
  red_flag_score = 0.2 if query contains a red-flag keyword, else 0.0
```

**Priority Logic:**

| Query Contains | Prioritized Sections |
|---|---|
| `risk`, `threat`, `uncertainty`, `exposure`, `volatility`, `vulnerable` | `risk_factors`, `mda` |
| `legal` | `legal` |
| `auditor` | `auditor_notes` |
| `note` or `notes` | `notes` |
| (default) | All sections equally |

**Red-Flag Keywords:** `restatement`, `material weakness`, `going concern`, `default`

**Class: `RuleBasedRetriever`**

| Method | Description |
|---|---|
| `retrieve(query, sections, max_sections)` | Returns top `max_sections` `RetrievalResult` objects ranked by score. Default: top 2. |
| `explain_retrieval(query, sections)` | Returns a full `RetrievalExplanation` for UI visualization — includes query tokens, prioritized sections, and all ranked section details. |
| `_score_sections(query, sections)` | Internal scoring engine. Iterates all sections, computes scores, returns sorted list. |
| `_prioritize_sections(query_terms)` | Maps query token sets to priority section names. |
| `_keyword_score(query_terms, text)` | Calculates what fraction of query tokens appear in the section text. |
| `_tokenize(text)` | Splits text into a lowercase token set using regex `[a-zA-Z']+`. |

**Data classes:**
```
RetrievalResult(section: str, score: float, text: str)

RetrievalExplanation(
  query_terms: List[str]
  prioritized_sections: List[str]
  ranked_sections: List[Dict]  # Full scoring breakdown per section
)
```

---

### 6.5 LLM Interface — `llm/`

#### `llm/gemini_interface.py` — `GeminiClient`

**Purpose:** HTTP client wrapper for the Google Gemini API. Sends prompts and returns generated text.

**Class: `GeminiClient`**

| Parameter | Default | Description |
|---|---|---|
| `model` | `gemini-2.5-flash` | Gemini model variant to use |
| `base_url` | `https://generativelanguage.googleapis.com` | Gemini API base URL |
| `api_key` | From env var `GEMINI_API_KEY` | Authentication key |

| Method | Description |
|---|---|
| `generate(prompt, temperature)` | POSTs to the Gemini `generateContent` endpoint. Returns the text response or `None` on failure. |
| `_extract_text(data)` | Parses the Gemini API JSON response to extract the generated text from `candidates[0].content.parts[0].text`. |

**Request Configuration:**
- Temperature: `0.2` (low, for consistent/deterministic risk analysis)
- Timeout: `120` seconds
- API authentication: via `?key=` query parameter

**Error Handling:**
- Returns `None` if the API key is missing.
- Catches all HTTP and parsing exceptions, prints a warning, and returns `None`.

---

### 6.6 Risk Analysis — `analysis/risk_analyzer.py`

**Purpose:** The core analysis engine. Takes a block of retrieved text and produces a structured risk report — either via Gemini LLM or via a local heuristic fallback.

**Class: `RiskAnalyzer`**

| Parameter | Description |
|---|---|
| `llm_client` | An LLM client instance (e.g., `GeminiClient`) |
| `require_llm` | If `True`, raises `RuntimeError` when the LLM fails instead of falling back |

**Main Method: `analyze(text) -> RiskAnalysisResult`**

Decision flow:
1. If text is empty → returns empty result.
2. If `llm_client` is set → attempts `_analyze_with_llm(text)`.
3. If LLM returns a valid response → parses and returns it.
4. If LLM fails and `require_llm=True` → raises `RuntimeError`.
5. Otherwise → falls back to `_heuristic_analysis(text)`.

**LLM Prompt (sent to Gemini):**
> "You are a financial risk analyst. Extract the top risks, categorize them, identify red flags, and summarize. Return JSON with keys: top_risks (array), risk_categories (object with keys Financial, Operational, Market, Regulatory), red_flags (array), confidence_score (0–100), summary (string)..."

**Heuristic Analysis Methods:**

| Method | Logic |
|---|---|
| `_find_risky_sentences(text)` | Splits text into sentences; returns up to 50 sentences containing any of: `risk`, `uncertain`, `volatility`, `may`, `could`, `potential`, `threat` |
| `_extract_top_risks(text)` | Returns the first 10 risky sentences as top risks |
| `_categorize_risks(risks)` | Keyword-based assignment into Financial, Operational, Market, or Regulatory buckets |
| `_find_red_flags(text)` | Regex search for: `material weakness`, `going concern`, `restatement`, `significant doubt` |
| `_score_confidence(text, red_flags)` | `min(100, 40 + risk_count + len(red_flags) * 10)` |
| `_build_summary(risks, flags)` | Generates a simple text summary sentence |
| `_extract_json(text)` | Extracts the first `{...}` block from LLM output using regex |

**Data class: `RiskAnalysisResult`**
```
RiskAnalysisResult(
  top_risks: List[str]                   # Top identified risk statements
  risk_categories: Dict[str, List[str]]  # Risks grouped by category
  red_flags: List[str]                   # Critical warning phrases found
  confidence_score: int                  # 0–100 confidence rating
  summary: str                           # Human-readable summary
  risky_sentences: List[str]             # All sentences containing risk language
)
```

**Risk Category Keywords:**

| Category | Keywords |
|---|---|
| Financial | `liquidity`, `debt`, `cash`, `credit`, `financing` |
| Operational | `supply`, `operations`, `technology`, `cyber`, `staff` |
| Market | `competition`, `demand`, `pricing`, `market` |
| Regulatory | `regulation`, `compliance`, `legal`, `policy` |

---

### 6.7 Report Comparison — `analysis/comparison_engine.py`

**Purpose:** Compares two financial reports (e.g., last year's vs. this year's 10-K) to identify changes in risk disclosure.

**Class: `RiskComparisonEngine`**

**Main Method: `compare_reports(report_old, report_new) -> ComparisonResult`**

Takes two report dictionaries (each with keys `risk_factors`, `mda`, `notes`, `legal`, `auditor_notes`) and produces a `ComparisonResult`.

**Internal Analysis:**

| Analysis | Method | Description |
|---|---|---|
| New risks | `_compare_risks()` | Risk sentences in new report not present in old (using token overlap ≥55% or fuzzy ratio ≥80%) |
| Removed risks | `_compare_risks()` | Risk sentences in old report not found in new |
| Tone change | `_compare_tone()` | Counts positive vs. cautious words in MD&A; labels as "more optimistic", "more cautious", or "neutral" |
| Risk intensity | `_compare_risk_intensity()` | Counts risk keyword hits + warning phrase hits + document length factor; labels "increased", "decreased", or "stable" |
| New red flags | `_detect_red_flag_delta()` | Flags present in new report but not in old |
| Contradiction detection | `_has_contradiction()` | Flags if MD&A is heavily positive (≥5 positive words) while risk section is heavily cautious (≥5 cautious words) |
| Vague language | `_detect_red_flags()` | Flags "increased vague language" if `may/could/might/potential/uncertain` appears ≥10 times |

**Matching Algorithm:**
Two risk sentences are considered a "match" (i.e., the same risk) if:
- Token overlap ≥ 55%, **OR**
- Jaccard similarity of token sets ≥ 80%

**Data class: `ComparisonResult`**
```
ComparisonResult(
  new_risks: List[str]                       # Risks appearing in new report only
  removed_risks: List[str]                   # Risks removed from new report
  tone_change: str                           # "more optimistic" / "more cautious" / "neutral"
  risk_intensity_change: str                 # "increased" / "decreased" / "stable"
  new_red_flags: List[str]                   # Critical new warning phrases
  highlighted_sentences: Dict[str, List[str]] # {"new": [...], "removed": [...]}
  confidence_score: int                      # 0–100
  summary: str                               # Plain-text comparison summary
)
```

---

### 6.8 Streamlit UI — `ui/app.py`

**Purpose:** Full-featured interactive web application built with Streamlit. Provides:
1. Single-report risk analysis.
2. Two-report comparison mode.
3. Vectorless RAG visualization panel.

**Key UI Sections:**

#### App Configuration (sidebar/top)
- Gemini model name input field.
- API key input (password-masked, or reads from `GEMINI_API_KEY` env var).
- Warning shown if API key is missing.

#### Mode 1: Single Report Analysis
- User uploads a PDF or HTML file.
- User types a natural language query (e.g., "What are the main financial risks?").
- On submit:
  - File is parsed and split into sections.
  - Retriever fetches the most relevant sections.
  - Gemini analyzes the retrieved text.
  - Results displayed: top risks, risk categories, red flags, confidence score, summary, risky sentences.
  - Download button for JSON export.

#### Mode 2: Report Comparison
- User uploads two files (e.g., `company_2022.html` and `company_2023.html`).
- Year is auto-detected from filename.
- The older and newer reports are automatically identified.
- Comparison engine runs.
- Results displayed: new risks, removed risks, tone change, intensity change, new red flags.

#### Vectorless RAG Visualization Panel (`_render_vectorless_rag_view`)
Expander panel titled "How Vectorless RAG Stores This Report" containing:
- **4 metrics:** raw text chars, stored sections count, retrieved sections count, context chars sent.
- **4-column pipeline view:** Parse → Store → Retrieve → Analyze.
- **Interactive retrieval flow diagram** (HTML/CSS rendered inline): Query → Prioritize → Rank → Fetch → Gemini.
- **Fetch trace:** query tokens, prioritized sections, ranked section cards with scores.
- **Worked example** explanation of how data was found.

**Internal Helper Functions:**

| Function | Description |
|---|---|
| `_parse_upload(uploaded_file)` | Saves upload to a temp file, parses it, returns (sections, cleaned_text) |
| `_extract_year(name)` | Extracts 4-digit year from a filename using regex |
| `_build_report_payload(name, sections)` | Builds the dict passed to the comparison engine |
| `_missing_section_warnings(sections)` | Shows Streamlit warnings if key sections are empty |
| `_json_download_button(data, label)` | Renders a Streamlit download button for JSON export |
| `_section_stats(sections)` | Computes character count and percentage share per section |
| `_highlight_terms(text, terms, limit)` | Wraps matched terms in `[[...]]` brackets in a text snippet |

---

## 7. End-to-End Data Flow

Below is a complete walkthrough of what happens when a user analyzes a filing:

```
Step 1: User Input
  └─▶ User uploads apple_2023.html
  └─▶ User types query: "What are the main risks?"
  └─▶ User clicks "Analyze"

Step 2: File Parsing (parser/)
  └─▶ SEC10KHtmlParser.parse(file_path)
      ├─ Reads HTML file
      ├─ Strips noise (script, style, nav, hidden elements)
      ├─ Extracts heading + paragraph blocks
      └─ Returns clean plain text (e.g., 850,000 characters)

Step 3: Section Segmentation (segmentation/)
  └─▶ SectionSplitter.split(cleaned_text)
      ├─ Scans each line for section header patterns (regex)
      ├─ Records character offsets of each detected section start
      └─ Returns Dict:
          {
            "risk_factors": "...Item 1A text...",
            "mda": "...Item 7 text...",
            "notes": "...Item 8 text...",
            "legal": "...Item 3 text...",
            "auditor_notes": "...",
            "other": ""
          }

Step 4: Rule-Based Retrieval (retrieval/)
  └─▶ RuleBasedRetriever.retrieve(query, sections, max_sections=2)
      ├─ Tokenizes query: {"what", "are", "the", "main", "risks"}
      ├─ "risks" → priority sections: ["risk_factors", "mda"]
      ├─ Scores each section:
      │   risk_factors: base=1.0, keyword=0.2, red_flag=0.0, total=1.2
      │   mda:          base=1.0, keyword=0.0, red_flag=0.0, total=1.0
      │   notes:        base=0.5, keyword=0.0, red_flag=0.0, total=0.5
      └─ Returns top 2: [risk_factors (1.2), mda (1.0)]

Step 5: LLM Analysis (llm/ + analysis/)
  └─▶ Combined text = risk_factors_text + "\n\n" + mda_text
  └─▶ RiskAnalyzer.analyze(combined_text)
      └─▶ GeminiClient.generate(prompt)
          ├─ Sends prompt with up to 12,000 chars of context to Gemini API
          └─ Returns JSON response

Step 6: Output Rendering
  └─▶ RiskAnalysisResult displayed in Streamlit:
      ├─ top_risks: ["Supply chain disruptions may...", "Foreign exchange volatility...", ...]
      ├─ risk_categories: {Financial: [...], Operational: [...], ...}
      ├─ red_flags: []
      ├─ confidence_score: 85
      ├─ summary: "Identified 12 risk statements with 0 red flags."
      └─ risky_sentences: [...]
```

---

## 8. Features & Capabilities

### 8.1 Single Report Analysis

Upload one PDF or HTML financial filing and receive:

| Output | Description |
|---|---|
| **Top Risks** | Up to 10 key risk statements extracted from the document |
| **Risk Categories** | Risks classified as Financial, Operational, Market, or Regulatory |
| **Red Flags** | Critical warnings: material weakness, going concern, restatement, significant doubt |
| **Confidence Score** | 0–100 score reflecting the richness and severity of risk language found |
| **Summary** | Concise text summary of findings |
| **Risky Sentences** | Up to 50 individual sentences containing risk-related language |
| **JSON Export** | Full structured output downloadable as a JSON file |

### 8.2 Report Comparison

Upload an older and a newer filing to detect:

| Comparison Output | Description |
|---|---|
| **New Risks** | Risk disclosures in the new report not present in the old |
| **Removed Risks** | Risk disclosures dropped from the old report |
| **Tone Change** | Whether management language shifted more optimistic or cautious |
| **Risk Intensity Change** | Whether the volume/severity of risk language increased or decreased |
| **New Red Flags** | Critical warnings that appeared for the first time |
| **Highlighted Sentences** | Side-by-side view of added/removed risk sentences |

### 8.3 Vectorless RAG Visualization

A dedicated in-app panel that exposes the entire retrieval pipeline:
- Parsed text statistics (character counts, section sizes)
- Section bucket storage view
- Retrieval scoring breakdown (base score, keyword score, red-flag score per section)
- Selected context character count
- Visual flow diagram (Query → Prioritize → Rank → Fetch → Gemini)
- Fetch trace with query tokens and section rankings

---

## 9. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | Python 3.x | Core programming language |
| Web UI | Streamlit | Interactive browser-based application |
| HTML Parsing | BeautifulSoup4 | SEC 10-K HTML document parsing |
| PDF Parsing (primary) | pdfplumber | PDF text and table extraction |
| PDF Parsing (fallback) | PyMuPDF (fitz) | Fallback PDF text extraction |
| HTTP Client | Requests | Gemini API HTTP calls |
| AI / LLM | Google Gemini API | Language model for risk analysis |
| Regex Engine | Python `re` | Pattern matching for section detection and risk terms |
| Testing | pytest | Unit testing |

---

## 10. Setup & Installation Guide

### Prerequisites
- Python 3.9 or higher
- A Google Gemini API key (obtain from [Google AI Studio](https://makersuite.google.com/))
- Internet access for Gemini API calls

### Step-by-Step Installation

**Step 1: Create and activate a virtual environment**

*Windows (PowerShell):*
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*macOS / Linux:*
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Step 2: Install dependencies**
```bash
pip install -r requirements.txt
pip install pytest
```

The `requirements.txt` contains:
```
streamlit
beautifulsoup4
pdfplumber
pymupdf
requests
```

**Step 3: Set the Gemini API key**

*Windows (PowerShell):*
```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

*macOS / Linux:*
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

Alternatively, the Streamlit UI includes a password-masked input field where you can paste the key at runtime without setting an environment variable.

---

## 11. Running the Application

### Streamlit Web Application (Recommended)

```bash
# Windows
.\.venv\Scripts\python.exe -m streamlit run ui\app.py

# macOS / Linux
python -m streamlit run ui/app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

**Quick Start in the UI:**
1. Paste your Gemini API key (or confirm it was loaded from the environment variable).
2. Upload a PDF or HTML financial report.
3. Type a query such as `"What are the main risks?"`.
4. Click **Analyze**.
5. Review results in the output panels.
6. Expand **"How Vectorless RAG Stores This Report"** to see the retrieval trace.

### Command-Line Interface (CLI)

```bash
# Analyze the included Apple 2023 sample filing
python main.py --file data/apple_2023.html --query "What are the main risks?" --model gemini-2.5-flash

# Analyze a custom PDF
python main.py --file path/to/filing.pdf --query "Are there any red flags?" --model gemini-2.5-flash
```

CLI output is printed to stdout as a JSON object containing all analysis fields.

---

## 12. Testing

Unit tests are located in the `tests/` directory and use `pytest`.

**Run all tests:**
```bash
# Windows
.\.venv\Scripts\python.exe -m pytest -q

# macOS / Linux
python -m pytest -q
```

**Current test coverage:**

| Test File | Tests |
|---|---|
| `tests/test_section_splitter.py` | `test_section_splitter_basic` — verifies that `risk_factors`, `mda`, and `legal` sections are correctly detected and populated from a sample multi-section text |

The test uses a synthetic text snippet containing standard SEC Item headers (`ITEM 1A`, `ITEM 7`, `ITEM 3`) and verifies the content of each detected section.

---

## 13. Configuration & Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes (or via UI) | Google Gemini API authentication key |

No other configuration files or environment variables are required. All other parameters (model name, file path, query) are provided via the UI or CLI arguments.

---

## 14. Input & Output Specification

### Supported Input Formats

| Format | Extension(s) | Parser Used |
|---|---|---|
| SEC 10-K HTML filing | `.html`, `.htm` | `SEC10KHtmlParser` (BeautifulSoup) |
| PDF financial report | `.pdf` | `PDFParser` (pdfplumber / PyMuPDF) |

**Input constraints:**
- File must be a real financial report with structured text content.
- PDF files must contain selectable text (not scanned images).
- HTML files should follow typical SEC EDGAR filing structure for best section detection.

### Output: Single Report Analysis

```json
{
  "sections": {
    "risk_factors": "...extracted section text...",
    "mda": "...extracted section text...",
    "notes": "",
    "legal": "",
    "auditor_notes": "",
    "other": ""
  },
  "top_risks": [
    "The company faces significant market risk due to currency volatility.",
    "Supply chain disruptions could materially impact operations."
  ],
  "risk_categories": {
    "Financial": ["..."],
    "Operational": ["..."],
    "Market": ["..."],
    "Regulatory": ["..."]
  },
  "red_flags": ["going concern"],
  "confidence_score": 78,
  "summary": "Identified 12 risk statements with 1 red flag.",
  "risky_sentences": ["...", "...", "..."]
}
```

### Output: Report Comparison

```json
{
  "new_risks": ["New supply chain risk not in prior filing..."],
  "removed_risks": ["Prior year pandemic risk no longer mentioned..."],
  "tone_change": "more cautious",
  "risk_intensity_change": "increased",
  "new_red_flags": ["material weakness"],
  "highlighted_sentences": {
    "new": ["..."],
    "removed": ["..."]
  },
  "confidence_score": 72,
  "summary": "New risks: 3. Removed risks: 1. Tone change: more cautious. Risk intensity: increased. New red flags: 1."
}
```

---

## 15. Security Considerations

| Risk | Mitigation |
|---|---|
| **API Key Exposure** | Key is never stored in source code. Loaded from environment variable or entered at runtime in a password-masked field. |
| **Source Control Leakage** | `.gitignore` should exclude `.env` files and virtual environments. The project's `CONTRIBUTING.md` explicitly prohibits committing secrets. |
| **Temporary File Handling** | Uploaded files are saved to system temp directories (`tempfile.NamedTemporaryFile`) and are not persisted beyond the session. |
| **LLM Prompt Injection** | User-supplied text is sent to Gemini as content (not as instructions). The prompt structure keeps user data in the `TEXT:` section, separate from the role/instruction prefix. |
| **External API Calls** | The only outbound connection is to `generativelanguage.googleapis.com` (Google's official API). All calls use HTTPS with a 120-second timeout. |

**Important:** If an API key has been accidentally committed to a public repository, it must be **rotated immediately** via the Google Cloud Console.

---

## 16. Current Limitations

| Limitation | Detail |
|---|---|
| **Heuristic Retrieval** | Section scoring is based on keyword rules, not semantic understanding. Edge cases with unusual document structure may retrieve suboptimal sections. |
| **Section Detection Dependency** | The section splitter relies on standard SEC 10-K Item headings (e.g., "ITEM 1A"). Non-standard or non-SEC documents may result in all content landing in the `other` bucket. |
| **LLM Context Window** | The analyzer sends only up to 12,000 characters of the retrieved text to Gemini, regardless of total document size. Very large sections may be truncated. |
| **Scanned PDFs** | The PDF parser cannot extract text from image-only (scanned) PDFs. The document must contain selectable/copyable text. |
| **No Persistence** | Analysis results are not saved to a database. Results exist only in the current Streamlit session. |
| **Test Coverage** | Currently only one test exists (`test_section_splitter_basic`). Parser, retriever, and analyzer modules lack formal test coverage. |
| **Internet Dependency** | Requires a live internet connection for all Gemini API calls. Offline/air-gapped usage is not supported. |

---

## 17. Roadmap & Future Enhancements

| Enhancement | Priority | Description |
|---|---|---|
| **Expanded test coverage** | High | Unit and integration tests for parser, retriever, and analyzer modules |
| **Larger context window handling** | High | Chunking strategy to handle documents larger than the Gemini context limit |
| **Visual retrieval trace exports** | Medium | Export the retrieval flow diagram as PDF or PNG for reporting |
| **More filing formats** | Medium | Support for XBRL, DOCX, and plain text filings |
| **Parsed-document caching** | Medium | Cache parsed sections per file to avoid re-parsing on repeated analysis |
| **Chart-based retrieval analytics** | Medium | Interactive charts showing section sizes, risk scores, and keyword distributions |
| **Stronger comparison reporting** | Medium | Structured diff view with paragraph-level change tracking |
| **Multiple LLM backend support** | Low | Abstract LLM interface to support swappable backends (e.g., Anthropic Claude, OpenAI GPT) |
| **Batch processing** | Low | CLI support for analyzing multiple files in one run |

---

## 18. Glossary

| Term | Definition |
|---|---|
| **RAG** | Retrieval-Augmented Generation — an AI architecture where relevant context is retrieved from a knowledge source and given to an LLM before it generates output. |
| **Vectorless RAG** | A RAG variant that uses rule-based retrieval instead of vector embeddings, making every retrieval decision explicit and traceable. |
| **LLM** | Large Language Model — an AI model trained on large text corpora to understand and generate natural language (e.g., Google Gemini). |
| **SEC 10-K** | An annual financial report required by the U.S. Securities and Exchange Commission for publicly traded companies. Contains standardized sections like Risk Factors (Item 1A) and MD&A (Item 7). |
| **MD&A** | Management's Discussion and Analysis — SEC Item 7; a section where company management discusses financial results, risks, and future outlook. |
| **Red Flag** | A critical warning phrase in a financial filing (e.g., "going concern", "material weakness", "restatement") that signals elevated financial risk. |
| **Section Splitter** | The Axithor component (`SectionSplitter`) that detects and extracts named SEC report sections from plain text. |
| **Rule-Based Retriever** | The Axithor component (`RuleBasedRetriever`) that scores and ranks sections using keyword and priority rules rather than vector similarity. |
| **Gemini** | Google's family of large language models, used in this project via the `generativelanguage.googleapis.com` REST API. |
| **Streamlit** | An open-source Python framework for building interactive data applications deployable as web apps. |
| **Confidence Score** | A 0–100 integer produced by the analyzer reflecting how much risk language and red-flag content was found in the analyzed text. Higher = more risk content present. |
| **pdfplumber** | A Python library for PDF text and table extraction, built on pdfminer. |
| **PyMuPDF (fitz)** | A Python binding for the MuPDF rendering library, used as a fallback PDF text extractor. |
| **BeautifulSoup4** | A Python library for parsing HTML and XML documents, used here for SEC 10-K HTML filings. |

# Axithor Risk AI

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Repo](https://img.shields.io/badge/GitHub-Axithor_Risk_AI-181717?style=for-the-badge&logo=github)](https://github.com/jayaprakash2207/Axithor-Risk-AI)

An explainable **vectorless RAG** system for financial risk analysis.

Axithor Risk AI reads SEC-style HTML and PDF reports, extracts structured sections, retrieves the most relevant parts with a rule-based pipeline instead of embeddings, and uses Gemini to generate risk-focused insights. The result is a simpler, more transparent RAG workflow that is easier to inspect, debug, and demo.

## Highlights

- No vector database
- No embeddings pipeline
- Explainable rule-based retrieval
- Financial-report-focused section splitting
- Gemini-powered structured risk analysis
- Streamlit UI with a built-in vectorless RAG visualization panel
- Report comparison workflow for detecting changes in risk framing

## Why Vectorless RAG?

Many RAG systems hide retrieval logic behind embeddings and similarity search. This project keeps retrieval visible.

Instead of storing vectors, Axithor Risk AI stores:

1. cleaned plain text
2. named report sections
3. section relevance scores
4. retrieved context sent to Gemini

That means you can actually see:

- what was parsed
- how it was grouped
- what was retrieved
- why the model got that context

## How It Works

```text
Report File
   ->
HTML/PDF Parser
   ->
Cleaned Plain Text
   ->
Section Splitter
   ->
Named Section Buckets
   ->
Rule-Based Retriever
   ->
Top Matching Sections
   ->
Gemini
   ->
Risk Analysis Output
```

## Features

### Single Report Analysis

Upload one filing and get:

- top risks
- risk categories
- red flags
- confidence score
- concise summary
- highlighted risky sentences

### Report Comparison

Upload an older and newer filing to detect:

- new risks
- removed risks
- tone changes
- risk intensity changes
- new red flags

### Vectorless RAG Visualization

The UI includes a dedicated panel showing:

- parsed text size
- stored section buckets
- retrieval scores
- selected context passed to Gemini
- in-memory data shape

This makes the retrieval path easy to explain in demos, interviews, and project reviews.

## Example Questions

You can ask prompts like:

- `What are the main risks?`
- `What operational risks stand out?`
- `Are there any red flags in this filing?`
- `How has the company’s risk profile changed?`

## Project Structure

```text
.
|-- analysis/
|   |-- comparison_engine.py
|   `-- risk_analyzer.py
|-- data/
|   |-- apple_2023.html
|   `-- README.txt
|-- llm/
|   |-- gemini_interface.py
|   `-- ollama_interface.py
|-- parser/
|   |-- html_parser.py
|   `-- pdf_parser.py
|-- retrieval/
|   `-- rule_engine.py
|-- segmentation/
|   `-- section_splitter.py
|-- tests/
|   `-- test_section_splitter.py
|-- ui/
|   `-- app.py
|-- main.py
|-- requirements.txt
`-- README.md
```

## Architecture Snapshot

| Layer | File(s) | Responsibility |
|---|---|---|
| Parsing | `parser/html_parser.py`, `parser/pdf_parser.py` | Extract clean text from HTML and PDF |
| Segmentation | `segmentation/section_splitter.py` | Detect financial-report sections like `risk_factors` and `mda` |
| Retrieval | `retrieval/rule_engine.py` | Rank sections using rule-based keyword and section-priority logic |
| LLM | `llm/gemini_interface.py` | Send retrieved context to Gemini |
| Analysis | `analysis/risk_analyzer.py` | Produce risk summaries, categories, and red flags |
| Comparison | `analysis/comparison_engine.py` | Compare old vs new reports |
| UI | `ui/app.py` | Streamlit interface and vectorless-RAG visualization |

## Tech Stack

- Python
- Streamlit
- BeautifulSoup4
- pdfplumber
- PyMuPDF
- Requests
- Gemini API

## Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
python -m pip install pytest
```

## Gemini API Key

You can provide the Gemini API key in either of these ways:

### Option 1. Enter it in the Streamlit UI

The app includes a secure password-style field for the key.

### Option 2. Set an environment variable

```powershell
$env:GEMINI_API_KEY="your_key_here"
```

## Run the Project

### CLI mode

```powershell
.\.venv\Scripts\python.exe main.py --model gemini-2.5-flash
```

Example:

```powershell
.\.venv\Scripts\python.exe main.py --file data\apple_2023.html --query "What are the main risks?" --model gemini-2.5-flash
```

Available CLI arguments:

- `--file` path to a PDF or HTML report
- `--query` analysis question
- `--model` Gemini model name

### Streamlit app

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui\app.py
```

Then:

1. paste the Gemini API key
2. upload a PDF or HTML report
3. run analysis
4. open `How Vectorless RAG Stores This Report`

## Testing

Run the tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Sample Data

The repo currently includes:

- `data/apple_2023.html`

You can add more sample reports to the `data/` folder for local testing.

## What Makes This Useful

- Great for explainable RAG demos
- Useful for SEC filing analysis prototypes
- Easier to debug than embedding-heavy pipelines
- Good learning project for document parsing and retrieval
- Strong base for building deeper financial AI workflows

## Current Limitations

- Retrieval is heuristic rather than embedding-based
- Section detection depends on common SEC-style headings
- Output quality depends on parsed text quality and Gemini responses
- Test coverage is still minimal

## Roadmap Ideas

- richer parser and retriever tests
- visual retrieval trace exports
- more filing formats
- parsed-document caching
- chart-based retrieval analytics
- stronger comparison reporting

## Security Note

Do not commit API keys to source control. Use environment variables or the Streamlit key field for local testing. If a key has been exposed publicly, rotate it immediately.

## Repository Status

This repository is actively set up for:

- local development
- GitHub publishing
- interactive Streamlit demos
- explainable vectorless RAG experiments

## License

No license file has been added yet.

If you want to open this project publicly for reuse, add a license such as MIT.

# Financial Risk Intelligence Assistant

A lightweight, explainable **vectorless RAG** app for financial report analysis.

This project extracts text from SEC-style HTML and PDF reports, splits the content into meaningful sections, retrieves the most relevant sections with rules instead of embeddings, and uses Gemini to generate structured risk analysis.

## Why This Project?

Most RAG demos jump straight to vector databases and embeddings.

This project takes a different route:

- No vector database
- No embeddings pipeline
- No opaque retrieval layer
- Clear, inspectable section-based ranking

That makes it easier to understand, debug, and visualize how retrieval works for structured financial documents.

## What It Does

- Parses HTML and PDF annual reports
- Cleans and normalizes raw report text
- Splits reports into sections like:
  - `risk_factors`
  - `mda`
  - `notes`
  - `legal`
  - `auditor_notes`
- Retrieves the most relevant sections for a user query with a rule-based retriever
- Uses Gemini to produce:
  - top risks
  - categorized risks
  - red flags
  - confidence score
  - summary
- Includes a Streamlit UI for:
  - single report analysis
  - report comparison
  - vectorless RAG visualization

## Key Idea: What "Vectorless RAG" Means Here

Instead of storing embeddings, this project stores:

1. Cleaned plain text from the uploaded report
2. Named section buckets created by heuristic section splitting
3. Retrieval scores from a rule-based matcher
4. Concatenated top sections sent to Gemini as context

So the retrieval flow is:

`Report -> Parsed Text -> Section Splitter -> Rule-Based Retrieval -> Gemini Analysis`

This makes the pipeline easier to inspect and explain than a traditional embedding-based RAG setup.

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

## Features

### 1. Single Report Analysis

Upload a PDF or HTML filing and ask:

- What are the main risks?
- Are there any red flags?
- What operational concerns stand out?

The app retrieves the most relevant sections, sends them to Gemini, and returns a structured answer.

### 2. Compare Reports

Upload an older and newer report to detect:

- new risks
- removed risks
- tone change
- intensity change
- red flag deltas

### 3. Vectorless RAG Visualization

The Streamlit app includes a dedicated panel that shows:

- raw parsed text size
- section buckets stored in memory
- retrieval scores
- selected context passed to Gemini
- in-memory JSON-like structure

This is especially useful for demos, interviews, and learning how non-vector retrieval works.

## Tech Stack

- Python
- Streamlit
- BeautifulSoup4
- pdfplumber
- PyMuPDF
- Requests
- Gemini API

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

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

The Streamlit app now supports entering the Gemini API key directly in the UI using a password field.

You can also set it as an environment variable before launching:

```powershell
$env:GEMINI_API_KEY="your_key_here"
```

## Running the Project

### Run the CLI pipeline

```powershell
.\.venv\Scripts\python.exe main.py --model gemini-2.5-flash
```

Optional arguments:

- `--file`: path to a PDF or HTML report
- `--query`: analysis question
- `--model`: Gemini model name

Example:

```powershell
.\.venv\Scripts\python.exe main.py --file data\apple_2023.html --query "What are the main risks?" --model gemini-2.5-flash
```

### Run the Streamlit app

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui\app.py
```

Then:

1. Paste your Gemini API key into the `Gemini API key` field
2. Upload a report
3. Click `Analyze Report`
4. Open `How Vectorless RAG Stores This Report`

## Example Workflow

1. Load a report from `data/` or upload your own PDF/HTML filing
2. Parse the document into clean plain text
3. Split the text into semantic report sections
4. Rank sections based on the user query
5. Send the top sections to Gemini
6. Return structured risk analysis and visualization

## Testing

Run the existing tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Current test coverage includes the section splitter baseline behavior.

## Sample Data

The repository includes:

- `data/apple_2023.html`

You can also place your own sample reports in [data/README.txt](/c:/vectorless%20rag/data/README.txt).

## Architecture Notes

### Parsing

- `parser/html_parser.py` extracts heading and paragraph blocks from SEC-style HTML
- `parser/pdf_parser.py` extracts text from PDF pages with `pdfplumber`, falling back to `PyMuPDF`

### Segmentation

- `segmentation/section_splitter.py` detects common filing sections using regex-based heading patterns

### Retrieval

- `retrieval/rule_engine.py` scores sections using keyword overlap and section prioritization
- No embeddings are generated or stored

### Analysis

- `analysis/risk_analyzer.py` sends retrieved context to Gemini and expects structured JSON output
- If no valid LLM result is returned, heuristic analysis is available in code as a fallback path

### Comparison

- `analysis/comparison_engine.py` compares older and newer report language to identify changes in risk framing

## Good Fit For

- financial document QA demos
- explainable RAG experiments
- SEC filing analysis
- educational RAG projects
- lightweight retrieval systems without vector infrastructure

## Limitations

- Retrieval is heuristic, not semantic embedding-based
- Section extraction depends on common SEC-like headings
- Output quality depends on report quality and Gemini response quality
- Test coverage is still minimal

## Next Ideas

- add richer tests for parser, retriever, and comparison engine
- export visual retrieval traces
- support more filing formats
- add local caching for parsed reports
- add charts for section weights and retrieval ranking

## Security Note

Do not commit API keys to source control. Use the Streamlit password field or environment variables for local testing, and rotate exposed keys if they were shared publicly.

## License

Add a license file if you plan to publish or share this project.

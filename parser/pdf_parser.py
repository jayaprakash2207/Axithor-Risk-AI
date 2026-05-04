import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ParsedDocument:
    text: str
    pages: List[str]
    tables: Optional[List[List[List[str]]]] = None


class PDFParser:
    def __init__(self, extract_tables: bool = False) -> None:
        self.extract_tables = extract_tables

    def parse(self, file_path: str) -> ParsedDocument:
        pages: List[str] = []
        tables: List[List[List[str]]] = []

        try:
            import pdfplumber  # type: ignore

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    pages.append(page_text)
                    if self.extract_tables:
                        page_tables = page.extract_tables() or []
                        tables.extend(page_tables)
        except Exception:
            try:
                import fitz  # type: ignore

                doc = fitz.open(file_path)
                for page in doc:
                    pages.append(page.get_text() or "")
            except Exception as exc:
                raise RuntimeError("Failed to parse PDF with pdfplumber or PyMuPDF") from exc

        full_text = "\n".join(pages)
        cleaned_text = self._clean_text(full_text)
        print(f"PDFParser: pages={len(pages)} text length={len(cleaned_text)}")
        return ParsedDocument(text=cleaned_text, pages=pages, tables=tables or None)

    def _clean_text(self, text: str) -> str:
        text = text.replace("\u00a0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

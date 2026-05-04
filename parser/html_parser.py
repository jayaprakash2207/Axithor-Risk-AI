import re
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup

import re
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup


@dataclass
class HtmlBlock:
    kind: str
    text: str


def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class SEC10KHtmlParser:
    def __init__(self) -> None:
        self.heading_pattern = re.compile(r"^item\s+\d+[a-z]?\b", re.IGNORECASE)

    def parse(self, file_path: str, return_blocks: bool = False) -> str | List[HtmlBlock]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                html = handle.read()
        except Exception as exc:
            print(f"SEC10KHtmlParser: failed to read file ({exc})")
            return [] if return_blocks else ""

        print(f"SEC10KHtmlParser: loaded HTML bytes={len(html)}")
        if not html.strip():
            print("SEC10KHtmlParser: empty HTML content")
            return [] if return_blocks else ""

        try:
            soup = BeautifulSoup(html, "html.parser")
            self._strip_noise(soup)
            blocks = self._extract_blocks(soup)
            print(f"SEC10KHtmlParser: extracted blocks={len(blocks)}")
        except Exception as exc:
            print(f"SEC10KHtmlParser: parse failed ({exc})")
            return [] if return_blocks else ""

        if return_blocks:
            return blocks

        cleaned = self._blocks_to_text(blocks)
        print(f"SEC10KHtmlParser: cleaned text length={len(cleaned)}")
        return cleaned

    def _strip_noise(self, soup: BeautifulSoup) -> None:
        if soup is None:
            raise ValueError("Parsed HTML is empty or invalid.")

        for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "svg"]):
            tag.decompose()

        for tag in soup.find_all(True):
            if tag is None:
                continue
            attrs = getattr(tag, "attrs", None)
            if not isinstance(attrs, dict):
                continue

            aria_hidden = str(attrs.get("aria-hidden", "")).lower()
            if aria_hidden == "true":
                tag.decompose()
                continue

            style_value = attrs.get("style")
            if style_value:
                style_text = str(style_value).replace(" ", "").lower()
                if "display:none" in style_text:
                    tag.decompose()

    def _extract_blocks(self, soup: BeautifulSoup) -> List[HtmlBlock]:
        blocks: List[HtmlBlock] = []
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
            text = self._clean_text(tag.get_text(" ", strip=True))
            if not text:
                continue

            kind = "heading" if tag.name.startswith("h") or self.heading_pattern.match(text) else "paragraph"
            blocks.append(HtmlBlock(kind=kind, text=text))

        if not blocks:
            blocks = self._extract_fallback_blocks(soup)

        return blocks

    def _extract_fallback_blocks(self, soup: BeautifulSoup) -> List[HtmlBlock]:
        raw_text = soup.get_text("\n", strip=True)
        lines = [self._clean_text(line) for line in raw_text.splitlines()]
        blocks: List[HtmlBlock] = []

        for line in lines:
            if not line:
                continue
            if len(line) < 5:
                continue

            is_heading = bool(self.heading_pattern.match(line)) or (line.isupper() and len(line) >= 8)
            kind = "heading" if is_heading else "paragraph"
            blocks.append(HtmlBlock(kind=kind, text=line))

        return blocks

    def _blocks_to_text(self, blocks: List[HtmlBlock]) -> str:
        lines: List[str] = []
        for block in blocks:
            if block.kind == "heading":
                lines.append(block.text.upper())
            else:
                lines.append(block.text)
        return self._normalize_lines(lines)

    def _clean_text(self, text: str) -> str:
        text = text.replace("\u00a0", " ")
        return clean_text(text)

    def _normalize_lines(self, lines: List[str]) -> str:
        joined = "\n".join(lines)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        return joined.strip()


def parse_html(file_path: str) -> str:
    return SEC10KHtmlParser().parse(file_path)

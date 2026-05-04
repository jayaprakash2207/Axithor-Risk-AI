import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class SectionMatch:
    name: str
    start: int
    end: int


class SectionSplitter:
    def __init__(self) -> None:
        self.section_patterns = {
            "risk_factors": [
                r"^\s*item\s+1a\b",
                r"^\s*item\s+1a\.?\s*[:.-]?\s*risk factors\b",
                r"^\s*risk factors\b",
            ],
            "mda": [
                r"^\s*item\s+7\b",
                r"^\s*item\s+7\.?\s*[:.-]?\s+management[' ]s discussion and analysis\b",
                r"^\s*management[' ]s discussion and analysis\b",
            ],
            "notes": [
                r"^\s*notes to (the )?financial statements\b",
                r"^\s*item\s+8\b",
                r"^\s*item\s+8\.?\s*[:.-]?\s+financial statements\b",
            ],
            "legal": [
                r"^\s*item\s+3\b",
                r"^\s*item\s+3\.?\s*[:.-]?\s+legal proceedings\b",
                r"^\s*legal proceedings\b",
            ],
            "auditor_notes": [
                r"^\s*report of independent registered public accounting firm\b",
                r"^\s*independent auditor[' ]s report\b",
            ],
        }

        self.heading_regex = re.compile(r"^[A-Z0-9][A-Z0-9 \-,:&'./]{5,}$")

    def split(self, text: str) -> Dict[str, str]:
        text = text or ""
        print(f"SectionSplitter: text length={len(text)}")
        matches = self._find_matches(text)
        sections = self._build_sections(text, matches)
        print(f"SectionSplitter: detected sections={len(matches)}")
        print({name: len(content) for name, content in sections.items()})
        return sections

    def _find_matches(self, text: str) -> List[SectionMatch]:
        if not text:
            return []
        lines = text.splitlines()
        offsets: List[int] = []
        cursor = 0
        for line in lines:
            offsets.append(cursor)
            cursor += len(line) + 1

        matches: List[SectionMatch] = []
        for index, line in enumerate(lines):
            normalized = re.sub(r"\s+", " ", line).strip()
            if not normalized:
                continue

            for name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, normalized, re.IGNORECASE | re.DOTALL):
                        start = offsets[index]
                        matches.append(SectionMatch(name=name, start=start, end=start))
                        break

            if self.heading_regex.match(normalized):
                for name, patterns in self.section_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, normalized, re.IGNORECASE | re.DOTALL):
                            start = offsets[index]
                            matches.append(SectionMatch(name=name, start=start, end=start))
                            break

        deduped = self._dedupe_matches(matches)
        return sorted(deduped, key=lambda m: m.start)

    def _dedupe_matches(self, matches: List[SectionMatch]) -> List[SectionMatch]:
        seen = set()
        deduped: List[SectionMatch] = []
        for match in matches:
            key = (match.name, match.start)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(match)
        return deduped

    def _build_sections(self, text: str, matches: List[SectionMatch]) -> Dict[str, str]:
        sections: Dict[str, str] = {
            "risk_factors": "",
            "mda": "",
            "notes": "",
            "legal": "",
            "auditor_notes": "",
            "other": "",
        }

        if not matches:
            sections["other"] = text[:5000]
            return sections

        spans: List[Tuple[str, int, int]] = []
        for idx, match in enumerate(matches):
            start = match.start
            end = matches[idx + 1].start if idx + 1 < len(matches) else len(text)
            spans.append((match.name, start, end))

        for name, start, end in spans:
            chunk = text[start:end].strip()
            if not sections.get(name):
                sections[name] = chunk
            else:
                sections[name] = sections[name] + "\n" + chunk

        covered = ["risk_factors", "mda", "notes", "legal", "auditor_notes"]
        if not any(sections[name] for name in covered):
            sections["other"] = text[:5000]

        return sections


def split_sections(text: str) -> Dict[str, str]:
    splitter = SectionSplitter()
    return splitter.split(text or "")

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class RetrievalResult:
    section: str
    score: float
    text: str


class RuleBasedRetriever:
    def __init__(self) -> None:
        self.risk_keywords = {"risk", "threat", "uncertainty", "exposure", "volatility", "vulnerable"}
        self.red_flag_keywords = {"restatement", "material weakness", "going concern", "default"}

    def retrieve(self, query: str, sections: Dict[str, str], max_sections: int = 2) -> List[RetrievalResult]:
        candidates = self._score_sections(query, sections)
        print(f"RuleBasedRetriever: query='{query}' candidates={len(candidates)}")
        return candidates[:max_sections]

    def _score_sections(self, query: str, sections: Dict[str, str]) -> List[RetrievalResult]:
        query_terms = self._tokenize(query)
        prioritized_sections = self._prioritize_sections(query_terms)

        results: List[RetrievalResult] = []
        for section_name, text in sections.items():
            if not text:
                continue
            base_score = 1.0 if section_name in prioritized_sections else 0.5
            keyword_score = self._keyword_score(query_terms, text)
            red_flag_score = 0.2 if self.red_flag_keywords & query_terms else 0.0
            total_score = base_score + keyword_score + red_flag_score
            results.append(RetrievalResult(section=section_name, score=total_score, text=text))

        return sorted(results, key=lambda r: r.score, reverse=True)

    def _prioritize_sections(self, query_terms: set) -> List[str]:
        if query_terms & self.risk_keywords:
            return ["risk_factors", "mda"]
        if "legal" in query_terms:
            return ["legal"]
        if "auditor" in query_terms:
            return ["auditor_notes"]
        if "note" in query_terms or "notes" in query_terms:
            return ["notes"]
        return ["risk_factors", "mda", "notes", "legal", "auditor_notes"]

    def _keyword_score(self, query_terms: set, text: str) -> float:
        if not query_terms:
            return 0.0
        matches = 0
        text_lower = text.lower()
        for term in query_terms:
            if term in text_lower:
                matches += 1
        return matches / max(len(query_terms), 1)

    def _tokenize(self, text: str) -> set:
        tokens = re.findall(r"[a-zA-Z']+", text.lower())
        return set(tokens)

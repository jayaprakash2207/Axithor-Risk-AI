import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ComparisonResult:
    new_risks: List[str]
    removed_risks: List[str]
    tone_change: str
    risk_intensity_change: str
    new_red_flags: List[str]
    highlighted_sentences: Dict[str, List[str]]
    confidence_score: int
    summary: str


class RiskComparisonEngine:
    def __init__(self) -> None:
        self.cautious_words = {"may", "could", "uncertain", "risk", "adverse", "volatility", "threat"}
        self.positive_words = {"strong", "growth", "opportunity", "improved", "resilient", "solid"}
        self.risk_keywords = {
            "risk",
            "uncertain",
            "volatility",
            "adverse",
            "threat",
            "exposure",
            "liquidity",
            "default",
        }
        self.warning_phrases = {"material weakness", "going concern", "significant doubt", "restatement"}

    def compare_reports(self, report_old: Dict[str, str], report_new: Dict[str, str]) -> ComparisonResult:
        old_risks = self._extract_risk_sentences(report_old.get("risk_factors", ""))
        new_risks = self._extract_risk_sentences(report_new.get("risk_factors", ""))

        new_only, removed_only, highlighted = self._compare_risks(old_risks, new_risks)
        tone_change = self._compare_tone(report_old.get("mda", ""), report_new.get("mda", ""))
        intensity_change = self._compare_risk_intensity(
            report_old.get("risk_factors", ""), report_new.get("risk_factors", "")
        )
        new_red_flags = self._detect_red_flag_delta(report_old, report_new)
        confidence_score = self._score_confidence(new_only, removed_only, new_red_flags)
        summary = self._build_summary(new_only, removed_only, tone_change, intensity_change, new_red_flags)

        print(
            "RiskComparisonEngine: new_risks=%s removed_risks=%s new_flags=%s"
            % (len(new_only), len(removed_only), len(new_red_flags))
        )

        return ComparisonResult(
            new_risks=new_only,
            removed_risks=removed_only,
            tone_change=tone_change,
            risk_intensity_change=intensity_change,
            new_red_flags=new_red_flags,
            highlighted_sentences=highlighted,
            confidence_score=confidence_score,
            summary=summary,
        )

    def _extract_risk_sentences(self, text: str) -> List[str]:
        cleaned = self._normalize(text)
        raw_sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        sentences = [sentence.strip() for sentence in raw_sentences if sentence.strip()]
        return [sentence for sentence in sentences if self._has_risk_keyword(sentence)]

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^a-z0-9 .,!?'%-]", "", text)
        return text.strip()

    def _has_risk_keyword(self, sentence: str) -> bool:
        return any(keyword in sentence for keyword in self.risk_keywords)

    def _compare_risks(self, old_risks: List[str], new_risks: List[str]) -> Tuple[List[str], List[str], Dict[str, List[str]]]:
        new_only = []
        removed_only = []
        highlighted = {"new": [], "removed": []}

        for candidate in new_risks:
            if not self._has_match(candidate, old_risks):
                new_only.append(candidate)
                highlighted["new"].append(candidate)

        for candidate in old_risks:
            if not self._has_match(candidate, new_risks):
                removed_only.append(candidate)
                highlighted["removed"].append(candidate)

        return new_only, removed_only, highlighted

    def _has_match(self, sentence: str, candidates: List[str]) -> bool:
        sentence_tokens = set(self._tokenize(sentence))
        if not sentence_tokens:
            return False

        for candidate in candidates:
            candidate_tokens = set(self._tokenize(candidate))
            if not candidate_tokens:
                continue
            overlap = len(sentence_tokens & candidate_tokens) / max(len(sentence_tokens), 1)
            if overlap >= 0.55:
                return True
            if self._fuzzy_ratio(sentence, candidate) >= 0.8:
                return True
        return False

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-z0-9']+", text.lower())

    def _fuzzy_ratio(self, a: str, b: str) -> float:
        a_set = set(self._tokenize(a))
        b_set = set(self._tokenize(b))
        if not a_set or not b_set:
            return 0.0
        return len(a_set & b_set) / len(a_set | b_set)

    def _compare_tone(self, old_mda: str, new_mda: str) -> str:
        old_score = self._tone_score(old_mda)
        new_score = self._tone_score(new_mda)

        if new_score - old_score > 3:
            return "more optimistic"
        if old_score - new_score > 3:
            return "more cautious"
        return "neutral"

    def _tone_score(self, text: str) -> int:
        tokens = self._tokenize(self._normalize(text))
        cautious = sum(1 for token in tokens if token in self.cautious_words)
        positive = sum(1 for token in tokens if token in self.positive_words)
        return positive - cautious

    def _compare_risk_intensity(self, old_text: str, new_text: str) -> str:
        old_score = self._intensity_score(old_text)
        new_score = self._intensity_score(new_text)
        delta = new_score - old_score

        if delta > 5:
            return "increased"
        if delta < -5:
            return "decreased"
        return "stable"

    def _intensity_score(self, text: str) -> int:
        normalized = self._normalize(text)
        tokens = self._tokenize(normalized)
        keyword_hits = sum(1 for token in tokens if token in self.risk_keywords)
        warning_hits = sum(1 for phrase in self.warning_phrases if phrase in normalized)
        length_factor = min(len(normalized) // 500, 10)
        return keyword_hits + warning_hits * 5 + length_factor

    def _detect_red_flag_delta(self, report_old: Dict[str, str], report_new: Dict[str, str]) -> List[str]:
        old_flags = self._detect_red_flags(report_old)
        new_flags = self._detect_red_flags(report_new)
        return [flag for flag in new_flags if flag not in old_flags]

    def _detect_red_flags(self, report: Dict[str, str]) -> List[str]:
        flags = []
        risk_text = self._normalize(report.get("risk_factors", ""))
        mda_text = self._normalize(report.get("mda", ""))

        for phrase in self.warning_phrases:
            if phrase in risk_text or phrase in mda_text:
                flags.append(phrase)

        if self._has_contradiction(mda_text, risk_text):
            flags.append("possible contradiction between mda and risk section")

        vague_phrases = ["may", "could", "might", "potential", "uncertain"]
        vague_count = sum(risk_text.count(phrase) for phrase in vague_phrases)
        if vague_count >= 10:
            flags.append("increased vague language")

        return list(dict.fromkeys(flags))

    def _has_contradiction(self, mda_text: str, risk_text: str) -> bool:
        positive_hits = sum(1 for word in self.positive_words if word in mda_text)
        cautious_hits = sum(1 for word in self.cautious_words if word in risk_text)
        return positive_hits >= 5 and cautious_hits >= 5

    def _score_confidence(self, new_risks: List[str], removed_risks: List[str], new_flags: List[str]) -> int:
        score = 50 + len(new_risks) * 5 + len(removed_risks) * 3 + len(new_flags) * 10
        return max(0, min(100, score))

    def _build_summary(
        self,
        new_risks: List[str],
        removed_risks: List[str],
        tone_change: str,
        intensity_change: str,
        new_flags: List[str],
    ) -> str:
        return (
            f"New risks: {len(new_risks)}. Removed risks: {len(removed_risks)}. "
            f"Tone change: {tone_change}. Risk intensity: {intensity_change}. "
            f"New red flags: {len(new_flags)}."
        )


def compare_reports(report_old: Dict[str, str], report_new: Dict[str, str]) -> ComparisonResult:
    engine = RiskComparisonEngine()
    return engine.compare_reports(report_old, report_new)

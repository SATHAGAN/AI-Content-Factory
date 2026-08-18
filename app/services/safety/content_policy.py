from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyResult:
    passed: bool
    risk_level: str
    matched_categories: list[str]
    reasons: list[str]


class BasicContentSafety:
    """Lightweight pre-publish safety gate.

    This is not a substitute for a dedicated safety classifier.
    """

    PATTERNS = {
        "self_harm": re.compile(r"\b(suicide|self[- ]harm|kill myself)\b", re.I),
        "graphic_violence": re.compile(r"\b(gore|dismember|decapitat)\w*\b", re.I),
        "sexual_content": re.compile(r"\b(explicit sexual|pornograph)\w*\b", re.I),
        "dangerous_instruction": re.compile(r"\b(make a bomb|build an explosive)\b", re.I),
    }

    def check(self, text: str) -> SafetyResult:
        matched = []
        for category, pattern in self.PATTERNS.items():
            if pattern.search(text):
                matched.append(category)

        if not matched:
            return SafetyResult(True, "low", [], [])

        level = "high" if len(matched) >= 1 else "low"
        return SafetyResult(
            False,
            level,
            matched,
            ["Potentially unsafe content requires review"],
        )

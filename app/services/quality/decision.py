from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityDecision:
    action: str
    score: float
    reasons: list[str]


class QualityGate:
    def __init__(self, minimum_score: float = 0.75):
        self.minimum_score = minimum_score

    def decide(
        self,
        media_qa_passed: bool,
        judge_score: float,
        safety_passed: bool,
    ) -> QualityDecision:
        if not safety_passed:
            return QualityDecision("block", judge_score, ["Safety gate failed"])

        if not media_qa_passed:
            return QualityDecision("regenerate", judge_score, ["Deterministic media QA failed"])

        if judge_score < self.minimum_score:
            return QualityDecision("regenerate", judge_score, ["Multimodal quality score is below threshold"])

        return QualityDecision("approve", judge_score, ["All quality gates passed"])

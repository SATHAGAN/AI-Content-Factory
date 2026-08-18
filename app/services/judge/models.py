from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class JudgeCriterion:
    name: str
    weight: float


DEFAULT_CRITERIA = (
    JudgeCriterion("prompt_alignment", 0.30),
    JudgeCriterion("visual_quality", 0.20),
    JudgeCriterion("character_consistency", 0.15),
    JudgeCriterion("narration_alignment", 0.15),
    JudgeCriterion("continuity", 0.10),
    JudgeCriterion("content_safety", 0.10),
)


@dataclass(frozen=True)
class JudgeIssue:
    criterion: str
    severity: str
    message: str
    evidence: str = ""
    scene_number: int | None = None


@dataclass
class JudgeReport:
    decision: str
    score: float
    threshold: float
    issues: list[JudgeIssue] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    regeneration: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "decision": self.decision,
            "score": round(self.score, 2),
            "threshold": self.threshold,
            "issues": [i.__dict__ for i in self.issues],
            "scores": self.scores,
            "regeneration": self.regeneration,
        }

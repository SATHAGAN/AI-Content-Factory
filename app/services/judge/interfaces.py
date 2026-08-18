from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class JudgeInput:
    source_text: str
    narration: str
    scene_prompt: str
    image_description: str | None = None
    transcript: str | None = None


@dataclass(frozen=True)
class JudgeResult:
    provider: str
    model_id: str
    score: float
    passed: bool
    reasons: list[str]
    warnings: list[str]
    raw: dict[str, Any]


class MultimodalJudge(Protocol):
    def evaluate(self, item: JudgeInput) -> JudgeResult:
        ...

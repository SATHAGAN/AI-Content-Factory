from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VLMRequest:
    prompt: str
    image_paths: list[str]


@dataclass(frozen=True)
class VLMResult:
    provider: str
    model_id: str
    scores: dict[str,float]
    issues: list[dict]
    decision: str
    raw: dict


class VisionLanguageModel(Protocol):
    def analyze(self, request: VLMRequest) -> VLMResult:
        ...

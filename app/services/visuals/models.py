from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

class VisualKind(str, Enum):
    IMAGE = "image"
    VIDEO = "video"

@dataclass(frozen=True)
class VisualRequest:
    job_id: str
    scene_id: str
    prompt: str
    duration_seconds: float
    width: int = 1080
    height: int = 1920
    fps: int = 24
    model: str | None = None
    kind: VisualKind = VisualKind.VIDEO
    negative_prompt: str | None = None
    metadata: dict = field(default_factory=dict)

@dataclass(frozen=True)
class VisualResult:
    job_id: str
    scene_id: str
    provider: str
    model: str
    kind: VisualKind
    output_path: str
    duration_seconds: float
    width: int
    height: int
    metadata: dict = field(default_factory=dict)

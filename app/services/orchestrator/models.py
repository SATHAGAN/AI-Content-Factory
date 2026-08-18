from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    CREATED="created"
    PLANNED="planned"
    GENERATING="generating"
    QA="qa"
    ASSEMBLING="assembling"
    COMPLETED="completed"
    FAILED="failed"


@dataclass(frozen=True)
class ProductionRequest:
    job_id: str
    channel_id: str
    source_text: str
    category: str
    language: str
    target_duration_seconds: float
    audience: str = "general"
    tone: str = "engaging"
    target_platforms: tuple = ()
    metadata: dict = field(default_factory=dict)


@dataclass
class ProductionResult:
    job_id: str
    status: JobStatus
    stage: str
    scene_count: int = 0
    final_video_path: str | None = None
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

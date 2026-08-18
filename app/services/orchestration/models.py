from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RepairRunStatus(str, Enum):
    READY = "ready"
    REPAIRING = "repairing"
    PASSED = "passed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


@dataclass(frozen=True)
class MediaState:
    audio_duration_seconds: float
    video_duration_seconds: float
    tts_speed: float = 1.0
    audio_path: str | None = None
    video_path: str | None = None
    final_path: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RepairRun:
    status: RepairRunStatus
    attempt: int
    state: MediaState
    action: str
    message: str
    history: tuple[dict, ...] = ()


@dataclass(frozen=True)
class OrchestrationPolicy:
    max_attempts: int = 3
    pass_delta_seconds: float = 0.35

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PersistentJobStatus(str, Enum):
    CREATED="created"
    RUNNING="running"
    PAUSED="paused"
    COMPLETED="completed"
    FAILED="failed"


class SceneStatus(str, Enum):
    PENDING="pending"
    RUNNING="running"
    COMPLETED="completed"
    FAILED="failed"


@dataclass(frozen=True)
class JobRecord:
    job_id: str
    channel_id: str
    status: PersistentJobStatus
    current_stage: str
    target_duration_seconds: float
    created_at: str
    updated_at: str
    error: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SceneRecord:
    job_id: str
    scene_id: str
    sequence: int
    status: SceneStatus
    attempts: int = 0
    video_path: str | None = None
    audio_path: str | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)

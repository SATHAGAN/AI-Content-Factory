from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class WorkerKind(str, Enum):
    CPU="cpu"
    GPU="gpu"


class WorkerStatus(str, Enum):
    STARTING="starting"
    IDLE="idle"
    BUSY="busy"
    DRAINING="draining"
    OFFLINE="offline"


@dataclass(frozen=True)
class WorkerCapabilities:
    worker_id: str
    kind: WorkerKind
    video: bool
    tts: bool
    qa: bool
    ffmpeg: bool
    vram_gb: float = 0.0
    models: tuple[str,...] = ()


@dataclass
class Worker:
    capabilities: WorkerCapabilities
    status: WorkerStatus = WorkerStatus.STARTING
    current_job_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class WorkerTask:
    task_id: str
    job_id: str
    task_type: str
    priority: int = 0
    required_capabilities: tuple[str,...] = ()
    preferred_models: tuple[str,...] = ()
    metadata: dict = field(default_factory=dict)

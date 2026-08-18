from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MediaOperation(str, Enum):
    TRIM_VIDEO = "trim_video"
    EXTEND_VIDEO = "extend_video"
    ADJUST_AUDIO_SPEED = "adjust_audio_speed"
    NORMALIZE_AUDIO = "normalize_audio"
    MERGE_AUDIO_VIDEO = "merge_audio_video"
    EXTRACT_AUDIO = "extract_audio"


@dataclass(frozen=True)
class MediaSpec:
    duration_seconds: float
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    sample_rate: int | None = None
    channels: int | None = None


@dataclass(frozen=True)
class MediaOperationRequest:
    operation: MediaOperation
    input_path: str
    output_path: str
    target_duration_seconds: float | None = None
    speed: float | None = None
    audio_path: str | None = None
    video_path: str | None = None
    normalize_loudness: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class MediaOperationResult:
    operation: MediaOperation
    output_path: str
    duration_seconds: float | None
    command: tuple[str, ...]
    metadata: dict = field(default_factory=dict)

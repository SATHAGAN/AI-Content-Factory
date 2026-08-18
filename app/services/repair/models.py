from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RepairAction(str, Enum):
    NONE="none"
    ADJUST_TTS_SPEED="adjust_tts_speed"
    EXTEND_VIDEO="extend_video"
    TRIM_VIDEO="trim_video"
    REGENERATE_AUDIO="regenerate_audio"
    REGENERATE_VIDEO="regenerate_video"
    MANUAL_REVIEW="manual_review"


@dataclass(frozen=True)
class RepairPolicy:
    max_tts_speed_delta: float = 0.15
    max_duration_delta_seconds: float = 0.35
    max_repair_attempts: int = 3
    prefer_tts_adjustment: bool = True
    allow_video_trim: bool = True
    allow_video_extension: bool = True
    allow_regeneration: bool = True


@dataclass(frozen=True)
class RepairRequest:
    audio_duration_seconds: float
    video_duration_seconds: float
    current_tts_speed: float = 1.0
    attempt: int = 0
    audio_regeneration_available: bool = True
    video_regeneration_available: bool = True


@dataclass(frozen=True)
class RepairPlan:
    action: RepairAction
    target_tts_speed: float | None = None
    target_video_duration_seconds: float | None = None
    reason: str = ""
    attempt: int = 0
    metadata: dict | None = None

    @property
    def retryable(self) -> bool:
        return self.action not in {
            RepairAction.NONE,
            RepairAction.MANUAL_REVIEW,
        }

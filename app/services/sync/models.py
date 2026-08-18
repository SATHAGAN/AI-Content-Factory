from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SyncStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass(frozen=True)
class MediaTiming:
    duration_seconds: float
    start_seconds: float = 0.0
    end_seconds: float | None = None

    @property
    def effective_end(self) -> float:
        return (
            self.end_seconds
            if self.end_seconds is not None
            else self.start_seconds + self.duration_seconds
        )


@dataclass(frozen=True)
class SyncConfig:
    max_duration_delta_seconds: float = 0.35
    warning_duration_delta_seconds: float = 0.15
    min_audio_duration_seconds: float = 0.20
    min_video_duration_seconds: float = 0.20
    require_nonempty_audio: bool = True
    require_nonempty_video: bool = True


@dataclass(frozen=True)
class SyncReport:
    status: SyncStatus
    audio_duration_seconds: float
    video_duration_seconds: float
    duration_delta_seconds: float
    score: float
    reasons: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == SyncStatus.PASS

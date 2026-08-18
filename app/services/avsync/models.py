from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SyncReport:
    video_duration_seconds: float
    audio_duration_seconds: float
    difference_seconds: float
    tolerance_seconds: float
    passed: bool
    action: str


def check_sync(
    video_duration_seconds: float,
    audio_duration_seconds: float,
    *,
    tolerance_seconds: float = 0.15,
) -> SyncReport:
    difference=abs(video_duration_seconds-audio_duration_seconds)
    passed=difference <= tolerance_seconds
    action="accept" if passed else "adjust_timeline"
    return SyncReport(
        video_duration_seconds=video_duration_seconds,
        audio_duration_seconds=audio_duration_seconds,
        difference_seconds=difference,
        tolerance_seconds=tolerance_seconds,
        passed=passed,
        action=action,
    )

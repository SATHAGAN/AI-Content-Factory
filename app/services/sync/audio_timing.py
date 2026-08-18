from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioTimingDecision:
    action: str
    target_duration_seconds: float
    audio_duration_seconds: float
    delta_seconds: float
    speed_factor: float


class AudioTimingPlanner:
    """Plans timing correction without changing source audio until render time."""

    def __init__(self, max_speedup: float = 1.20, max_slowdown: float = 0.85):
        self.max_speedup = max_speedup
        self.max_slowdown = max_slowdown

    def decide(self, target_duration_seconds: float, audio_duration_seconds: float) -> AudioTimingDecision:
        if target_duration_seconds <= 0 or audio_duration_seconds <= 0:
            raise ValueError("Durations must be positive")

        delta = audio_duration_seconds - target_duration_seconds
        tolerance = max(0.35, target_duration_seconds * 0.04)

        if abs(delta) <= tolerance:
            return AudioTimingDecision(
                "keep",
                target_duration_seconds,
                audio_duration_seconds,
                delta,
                1.0,
            )

        # atempo speed factor: >1 makes audio shorter, <1 makes audio longer
        desired = audio_duration_seconds / target_duration_seconds
        speed = min(self.max_speedup, max(self.max_slowdown, desired))

        if abs(desired - speed) > 0.01:
            return AudioTimingDecision(
                "regenerate_or_recut",
                target_duration_seconds,
                audio_duration_seconds,
                delta,
                speed,
            )

        return AudioTimingDecision(
            "time_stretch",
            target_duration_seconds,
            audio_duration_seconds,
            delta,
            speed,
        )

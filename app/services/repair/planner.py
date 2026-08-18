from __future__ import annotations

from app.services.repair.models import (
    RepairAction,
    RepairPlan,
    RepairPolicy,
    RepairRequest,
)


class RepairPlanner:
    """Select the smallest safe repair before full regeneration."""

    def __init__(self, policy: RepairPolicy | None = None):
        self.policy=policy or RepairPolicy()

    def plan(self, request: RepairRequest) -> RepairPlan:
        delta=round(
            request.audio_duration_seconds-request.video_duration_seconds,
            6,
        )

        if abs(delta) <= self.policy.max_duration_delta_seconds:
            return RepairPlan(
                action=RepairAction.NONE,
                reason="media_already_within_tolerance",
                attempt=request.attempt,
            )

        if request.attempt >= self.policy.max_repair_attempts:
            return RepairPlan(
                action=RepairAction.MANUAL_REVIEW,
                reason="maximum_repair_attempts_reached",
                attempt=request.attempt,
            )

        # Audio is longer: prefer modest speech-speed adjustment first.
        if delta > 0 and self.policy.prefer_tts_adjustment:
            target=(
                request.current_tts_speed
                * request.audio_duration_seconds
                / max(request.video_duration_seconds, 0.001)
            )
            lower=request.current_tts_speed-self.policy.max_tts_speed_delta
            upper=request.current_tts_speed+self.policy.max_tts_speed_delta
            target=max(lower,min(upper,target))

            if abs(target-request.current_tts_speed) <= self.policy.max_tts_speed_delta:
                return RepairPlan(
                    action=RepairAction.ADJUST_TTS_SPEED,
                    target_tts_speed=round(target,4),
                    reason="audio_longer_than_video",
                    attempt=request.attempt+1,
                    metadata={"delta_seconds":delta},
                )

        # Video longer: trimming is deterministic and safer than regeneration.
        if delta < 0 and self.policy.allow_video_trim:
            return RepairPlan(
                action=RepairAction.TRIM_VIDEO,
                target_video_duration_seconds=request.audio_duration_seconds,
                reason="video_longer_than_audio",
                attempt=request.attempt+1,
                metadata={"delta_seconds":delta},
            )

        if delta > 0 and self.policy.allow_video_extension:
            return RepairPlan(
                action=RepairAction.EXTEND_VIDEO,
                target_video_duration_seconds=request.audio_duration_seconds,
                reason="audio_longer_than_video",
                attempt=request.attempt+1,
                metadata={"delta_seconds":delta},
            )

        if self.policy.allow_regeneration:
            if request.audio_regeneration_available and delta > 0:
                return RepairPlan(
                    action=RepairAction.REGENERATE_AUDIO,
                    reason="audio_duration_cannot_be_adjusted_safely",
                    attempt=request.attempt+1,
                )
            if request.video_regeneration_available:
                return RepairPlan(
                    action=RepairAction.REGENERATE_VIDEO,
                    reason="video_duration_cannot_be_adjusted_safely",
                    attempt=request.attempt+1,
                )

        return RepairPlan(
            action=RepairAction.MANUAL_REVIEW,
            reason="no_safe_automatic_repair_available",
            attempt=request.attempt,
        )

from __future__ import annotations

from app.services.sync.models import SyncConfig, SyncReport, SyncStatus


class AVSyncAnalyzer:
    """Deterministic timing quality gate.

    This first implementation validates container-level timing. It intentionally
    does not claim phoneme-level lip-sync detection. That will be a later,
    model-backed quality layer.
    """

    def __init__(self, config: SyncConfig | None = None):
        self.config = config or SyncConfig()

    def analyze(
        self,
        *,
        audio_duration_seconds: float,
        video_duration_seconds: float,
        audio_present: bool = True,
        video_present: bool = True,
        metadata: dict | None = None,
    ) -> SyncReport:
        reasons: list[str] = []

        if self.config.require_nonempty_audio and not audio_present:
            return SyncReport(
                status=SyncStatus.FAIL,
                audio_duration_seconds=audio_duration_seconds,
                video_duration_seconds=video_duration_seconds,
                duration_delta_seconds=abs(
                    audio_duration_seconds - video_duration_seconds
                ),
                score=0.0,
                reasons=("audio_missing",),
                metadata=metadata or {},
            )

        if self.config.require_nonempty_video and not video_present:
            return SyncReport(
                status=SyncStatus.FAIL,
                audio_duration_seconds=audio_duration_seconds,
                video_duration_seconds=video_duration_seconds,
                duration_delta_seconds=abs(
                    audio_duration_seconds - video_duration_seconds
                ),
                score=0.0,
                reasons=("video_missing",),
                metadata=metadata or {},
            )

        if audio_duration_seconds < self.config.min_audio_duration_seconds:
            reasons.append("audio_too_short")

        if video_duration_seconds < self.config.min_video_duration_seconds:
            reasons.append("video_too_short")

        delta = round(abs(audio_duration_seconds - video_duration_seconds), 6)

        # Normalize timing quality to [0, 1]. The hard failure threshold is 0.
        if delta >= self.config.max_duration_delta_seconds:
            score = 0.0
        else:
            score = max(
                0.0,
                1.0 - (
                    delta / max(self.config.max_duration_delta_seconds, 1e-9)
                ),
            )

        if reasons:
            status = SyncStatus.FAIL
        elif delta >= self.config.max_duration_delta_seconds:
            reasons.append("duration_mismatch")
            status = SyncStatus.FAIL
        elif delta > self.config.warning_duration_delta_seconds:
            reasons.append("duration_mismatch_warning")
            status = SyncStatus.WARNING
        else:
            status = SyncStatus.PASS

        return SyncReport(
            status=status,
            audio_duration_seconds=audio_duration_seconds,
            video_duration_seconds=video_duration_seconds,
            duration_delta_seconds=delta,
            score=round(score, 4),
            reasons=tuple(reasons),
            metadata=metadata or {},
        )

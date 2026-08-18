from __future__ import annotations

from app.services.sync.analyzer import AVSyncAnalyzer
from app.services.sync.models import SyncReport
from app.services.sync.probe import FFProbeMediaProbe


class MediaSyncService:
    def __init__(
        self,
        analyzer: AVSyncAnalyzer | None = None,
        probe: FFProbeMediaProbe | None = None,
    ):
        self.analyzer = analyzer or AVSyncAnalyzer()
        self.probe = probe or FFProbeMediaProbe()

    def analyze_durations(
        self,
        *,
        audio_duration_seconds: float,
        video_duration_seconds: float,
        metadata: dict | None = None,
    ) -> SyncReport:
        return self.analyzer.analyze(
            audio_duration_seconds=audio_duration_seconds,
            video_duration_seconds=video_duration_seconds,
            metadata=metadata,
        )

    def analyze_files(
        self,
        *,
        audio_path: str,
        video_path: str,
        metadata: dict | None = None,
    ) -> SyncReport:
        audio_duration = self.probe.duration_seconds(audio_path)
        video_duration = self.probe.duration_seconds(video_path)
        return self.analyze_durations(
            audio_duration_seconds=audio_duration,
            video_duration_seconds=video_duration,
            metadata=metadata,
        )

from __future__ import annotations

from app.services.stt.models import STTResult, STTWord
from app.services.subtitles.models import SubtitleArtifact, SubtitleConfig
from app.services.subtitles.service import SubtitleService


class CaptionPipelineService:
    """Connect STT word timestamps directly to subtitle generation."""

    def __init__(self, subtitle_service: SubtitleService | None = None):
        self.subtitle_service = subtitle_service or SubtitleService()

    def generate_from_stt(
        self,
        stt_result: STTResult,
        output_path: str,
        config: SubtitleConfig | None = None,
    ) -> SubtitleArtifact:
        words = [
            STTWord(
                text=word.text,
                start_seconds=word.start_seconds,
                end_seconds=word.end_seconds,
                confidence=word.confidence,
            )
            for word in stt_result.words
        ]

        if not words:
            raise ValueError(
                "STT result contains no word timestamps; "
                "caption generation cannot be synchronized."
            )

        return self.subtitle_service.generate(
            words,
            output_path,
            config,
        )

    def generate_and_burn_in(
        self,
        stt_result: STTResult,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        config: SubtitleConfig | None = None,
    ):
        artifact = self.generate_from_stt(
            stt_result,
            subtitle_path,
            config,
        )
        command = self.subtitle_service.burn_in(
            video_path,
            artifact.path,
            output_path,
        )
        return artifact, command

from app.services.subtitles.ffmpeg import SubtitleBurnInEngine
from app.services.subtitles.models import SubtitleConfig, TranscriptWord
from app.services.subtitles.segmenter import TranscriptSegmenter
from app.services.subtitles.writer import SubtitleWriter


class SubtitleService:
    def __init__(
        self,
        segmenter: TranscriptSegmenter | None = None,
        writer: SubtitleWriter | None = None,
        burn_in_engine: SubtitleBurnInEngine | None = None,
    ):
        self.segmenter = segmenter or TranscriptSegmenter()
        self.writer = writer or SubtitleWriter()
        self.burn_in_engine = burn_in_engine or SubtitleBurnInEngine()

    def generate(
        self,
        words: list[TranscriptWord],
        output_path: str,
        config: SubtitleConfig | None = None,
    ):
        active_config = config or self.segmenter.config
        # Keep a supplied config authoritative.
        segmenter = TranscriptSegmenter(active_config)
        segments = segmenter.segment(words)
        return self.writer.write(
            segments,
            output_path,
            active_config.format,
        )

    def burn_in(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
    ):
        return self.burn_in_engine.execute(
            video_path,
            subtitle_path,
            output_path,
        )

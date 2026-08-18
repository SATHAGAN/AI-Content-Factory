from __future__ import annotations

from pathlib import Path

from app.services.rendering.assembly import VideoAssemblyService
from app.services.rendering.audio import AudioRenderService
from app.services.rendering.audio_timeline import AudioTimelineBuilder
from app.services.rendering.audio_timeline_ffmpeg import FFmpegNarrationTimeline
from app.services.rendering.subtitles import SubtitleRenderService
from app.services.rendering.sync_report import build_sync_report


class FinalRenderPipeline:
    """Render scene videos and a complete multi-scene narration timeline."""

    def __init__(
        self,
        assembler=None,
        audio=None,
        subtitles=None,
        timeline_builder=None,
        narration_renderer=None,
    ):
        self.assembler=assembler or VideoAssemblyService()
        self.audio=audio or AudioRenderService()
        self.subtitles=subtitles or SubtitleRenderService()
        self.timeline_builder=timeline_builder or AudioTimelineBuilder()
        self.narration_renderer=narration_renderer or FFmpegNarrationTimeline()

    def render(
        self,
        scene_assets: list[dict],
        output_dir: str,
        *,
        background_music: str | None = None,
        music_volume: float = 0.10,
        subtitles_srt: str | None = None,
    ) -> dict:
        if not scene_assets:
            raise ValueError("No scene assets supplied")

        directory=Path(output_dir)
        directory.mkdir(parents=True,exist_ok=True)
        ordered=sorted(scene_assets,key=lambda x:x["number"])

        assembled=str(directory/"01_assembled.mp4")
        self.assembler.assemble([x["video_path"] for x in ordered],assembled)

        timeline=self.timeline_builder.build(ordered)
        sync_report=build_sync_report(timeline)

        narration_path=None
        current=assembled
        if timeline.segments:
            narration_path=self.narration_renderer.render(
                timeline,str(directory/"02_narration.m4a")
            )
            current=self.audio.mux(current,narration_path,str(directory/"03_narrated.mp4"))

        if background_music:
            current=self.audio.add_background_music(
                current,background_music,str(directory/"04_music.mp4"),music_volume
            )

        if subtitles_srt:
            current=self.subtitles.burn_in(
                current,subtitles_srt,str(directory/"05_subtitled.mp4")
            )

        return {
            "video_path":current,
            "scene_count":len(ordered),
            "narration_path":narration_path,
            "narration_duration_seconds":timeline.duration_seconds,
            "sync_report":sync_report,
            "background_music":bool(background_music),
            "subtitles":bool(subtitles_srt),
            "status":"rendered",
        }

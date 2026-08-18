from __future__ import annotations

from dataclasses import dataclass

from app.services.render.audio_video import AudioVideoSyncService
from app.services.render.ffmpeg_render import VideoRenderService
from app.services.qa.video_checks import VideoQualityChecker


@dataclass(frozen=True)
class RenderResult:
    video_path: str
    qa: dict


class ProductionRenderPipeline:
    def __init__(
        self,
        renderer: VideoRenderService | None = None,
        muxer: AudioVideoSyncService | None = None,
        qa: VideoQualityChecker | None = None,
    ):
        self.renderer = renderer or VideoRenderService()
        self.muxer = muxer or AudioVideoSyncService()
        self.qa = qa or VideoQualityChecker()

    def render(
        self,
        scene_paths: list[str],
        output_path: str,
        audio_path: str | None = None,
    ) -> RenderResult:
        rendered = self.renderer.render_concat(scene_paths, output_path)

        final = rendered
        if audio_path:
            final = self.muxer.mux(rendered, audio_path, output_path + ".with-audio.mp4")

        qa = self.qa.check(final, require_audio=audio_path is not None)
        if not qa.passed:
            raise RuntimeError(f"Video QA failed: {qa.errors}")

        return RenderResult(video_path=final, qa=qa.to_dict())

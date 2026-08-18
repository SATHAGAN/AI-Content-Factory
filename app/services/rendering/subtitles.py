from __future__ import annotations

from pathlib import Path

from app.services.rendering.ffmpeg_adapter import FFmpegAdapter


class SubtitleRenderService:
    def __init__(self, ffmpeg: FFmpegAdapter | None = None):
        self.ffmpeg=ffmpeg or FFmpegAdapter()

    def burn_in(self, video_path: str, srt_path: str, output_path: str) -> str:
        output=Path(output_path)
        output.parent.mkdir(parents=True,exist_ok=True)
        self.ffmpeg.run([
            "-i",video_path,
            "-vf",f"subtitles={srt_path}",
            "-c:a","copy",
            str(output),
        ])
        return str(output)

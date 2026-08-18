from __future__ import annotations

import subprocess
from pathlib import Path

from app.services.media.ffmpeg import FFmpegError, FFmpegRunner


class VideoRenderService:
    def __init__(self, ffmpeg: FFmpegRunner | None = None):
        self.ffmpeg = ffmpeg or FFmpegRunner()

    def render_concat(self, scene_paths: list[str], output_path: str) -> str:
        if not scene_paths:
            raise ValueError("At least one scene is required")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        list_file = output.with_suffix(".concat.txt")

        # FFmpeg concat demuxer requires each path to be quoted.
        lines = []
        for scene in scene_paths:
            path = Path(scene).resolve()
            if not path.exists():
                raise FileNotFoundError(path)
            safe = str(path).replace("'", "'\\''")
            lines.append(f"file '{safe}'")
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        self.ffmpeg.concatenate(list_file, output)
        return str(output)

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class SubtitleBurnInEngine:
    def __init__(self, binary: str = "ffmpeg", dry_run: bool = False):
        self.binary = binary
        self.dry_run = dry_run

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    @staticmethod
    def _escape_filter_path(path: str) -> str:
        # FFmpeg filter arguments need escaping for backslash, colon and quotes.
        return (
            str(Path(path))
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
        )

    def build_command(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
    ) -> list[str]:
        if not self.dry_run:
            if not Path(video_path).is_file():
                raise FileNotFoundError(video_path)
            if not Path(subtitle_path).is_file():
                raise FileNotFoundError(subtitle_path)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        subtitle = self._escape_filter_path(subtitle_path)

        return [
            self.binary,
            "-hide_banner", "-loglevel", "error", "-y",
            "-i", video_path,
            "-vf", f"subtitles='{subtitle}'",
            "-c:v", "libx264",
            "-c:a", "copy",
            "-movflags", "+faststart",
            output_path,
        ]

    def execute(self, video_path: str, subtitle_path: str, output_path: str):
        command = self.build_command(video_path, subtitle_path, output_path)
        if self.dry_run:
            return command
        if not self.available():
            raise RuntimeError("FFmpeg is required for subtitle burn-in")
        subprocess.run(command, check=True)
        if not Path(output_path).is_file():
            raise RuntimeError("Subtitle burn-in completed without output")
        return command

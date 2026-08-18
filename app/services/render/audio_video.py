from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class AudioVideoSyncService:
    def __init__(self, ffmpeg: str = "ffmpeg"):
        self.ffmpeg = ffmpeg

    def mux(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        shortest: bool = True,
    ) -> str:
        if shutil.which(self.ffmpeg) is None:
            raise RuntimeError("ffmpeg not installed")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        command = [
            self.ffmpeg, "-y", "-i", video_path, "-i", audio_path,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac",
        ]
        if shortest:
            command.append("-shortest")
        command.append(str(output))

        result = subprocess.run(
            command, capture_output=True, text=True, timeout=900
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Audio/video mux failed")
        return str(output)

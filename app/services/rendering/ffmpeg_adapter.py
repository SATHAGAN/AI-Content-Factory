from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class FFmpegAdapter:
    def __init__(self, executable: str = "ffmpeg"):
        self.executable = executable

    def available(self) -> bool:
        return shutil.which(self.executable) is not None

    def run(self, args: list[str], timeout: int = 1800) -> None:
        if not self.available():
            raise RuntimeError("FFmpeg is not installed or not available on PATH")
        result = subprocess.run(
            [self.executable, "-y", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-4000:] or "FFmpeg command failed")

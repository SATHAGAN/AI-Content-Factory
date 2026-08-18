from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class FFProbeMediaProbe:
    """Reads media duration using ffprobe when available."""

    def __init__(self, ffprobe_binary: str = "ffprobe"):
        self.ffprobe_binary = ffprobe_binary

    def available(self) -> bool:
        return shutil.which(self.ffprobe_binary) is not None

    def duration_seconds(self, path: str) -> float:
        if not self.available():
            raise RuntimeError(
                "ffprobe is required to inspect media duration but was not found"
            )

        target = Path(path)
        if not target.is_file():
            raise FileNotFoundError(target)

        result = subprocess.run(
            [
                self.ffprobe_binary,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(target),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        payload = json.loads(result.stdout)
        duration = payload.get("format", {}).get("duration")
        if duration is None:
            raise ValueError(f"Duration not available for {target}")
        return float(duration)

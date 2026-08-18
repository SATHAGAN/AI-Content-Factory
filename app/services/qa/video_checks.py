from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class VideoQAResult:
    def __init__(self, passed: bool, duration_seconds: float | None, width: int | None,
                 height: int | None, fps: float | None, has_audio: bool, errors: list[str]):
        self.passed = passed
        self.duration_seconds = duration_seconds
        self.width = width
        self.height = height
        self.fps = fps
        self.has_audio = has_audio
        self.errors = errors

    def to_dict(self):
        return {
            "passed": self.passed,
            "duration_seconds": self.duration_seconds,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "has_audio": self.has_audio,
            "errors": self.errors,
        }


class VideoQualityChecker:
    def __init__(self, ffprobe: str = "ffprobe"):
        self.ffprobe = ffprobe

    def check(self, path: str, require_audio: bool = False) -> VideoQAResult:
        errors = []
        if shutil.which(self.ffprobe) is None:
            return VideoQAResult(False, None, None, None, None, False, ["ffprobe not installed"])

        target = Path(path)
        if not target.exists():
            return VideoQAResult(False, None, None, None, None, False, ["video file not found"])

        result = subprocess.run(
            [
                self.ffprobe, "-v", "error", "-show_streams", "-show_format",
                "-of", "json", str(target)
            ],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return VideoQAResult(False, None, None, None, None, False, [result.stderr.strip()])

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return VideoQAResult(False, None, None, None, None, False, ["invalid ffprobe JSON"])

        streams = data.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
        fmt = data.get("format", {})

        if not video:
            errors.append("no video stream")
        duration = float(fmt["duration"]) if fmt.get("duration") else None
        width = video.get("width") if video else None
        height = video.get("height") if video else None

        fps = None
        if video and video.get("r_frame_rate") and "/" in video["r_frame_rate"]:
            n, d = video["r_frame_rate"].split("/", 1)
            if float(d):
                fps = float(n) / float(d)

        if require_audio and not audio:
            errors.append("audio stream required but missing")

        if duration is not None and duration <= 0:
            errors.append("duration must be positive")

        return VideoQAResult(
            passed=not errors,
            duration_seconds=duration,
            width=width,
            height=height,
            fps=fps,
            has_audio=audio is not None,
            errors=errors,
        )

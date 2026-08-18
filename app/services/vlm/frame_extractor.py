from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class FrameExtractor:
    """Extract representative frames with FFmpeg.

    The extraction rate is configurable so long videos do not create an
    unnecessarily large vision-language-model input.
    """

    def __init__(self, ffmpeg: str = "ffmpeg"):
        self.ffmpeg=ffmpeg

    def extract(self, video_path: str, output_dir: str, *, fps: float = 1.0, max_frames: int = 12) -> list[str]:
        if fps <= 0:
            raise ValueError("fps must be positive")
        if max_frames < 1:
            raise ValueError("max_frames must be positive")
        if shutil.which(self.ffmpeg) is None:
            raise RuntimeError("FFmpeg is not installed or not available on PATH")

        directory=Path(output_dir)
        directory.mkdir(parents=True,exist_ok=True)
        pattern=directory/"frame_%03d.jpg"
        result=subprocess.run([
            self.ffmpeg,"-y","-i",video_path,
            "-vf",f"fps={fps}",
            "-frames:v",str(max_frames),
            "-q:v","3",str(pattern)
        ],capture_output=True,text=True,timeout=600)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-3000:] or "Frame extraction failed")
        return [str(p) for p in sorted(directory.glob("frame_*.jpg"))]

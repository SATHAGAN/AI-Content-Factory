import shutil
import subprocess
from pathlib import Path

import pytest

from app.services.qa.video_checks import VideoQualityChecker


def test_qa_missing_file():
    result = VideoQualityChecker().check("/does/not/exist.mp4")
    assert not result.passed
    assert "video file not found" in result.errors


def test_qa_requires_ffprobe_or_runs_real_probe(tmp_path):
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("FFmpeg/ffprobe not installed")

    video = tmp_path / "sample.mp4"
    command = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=160x120:d=1",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-shortest", "-c:v", "libx264", "-c:a", "aac", str(video)
    ]
    subprocess.run(command, check=True, capture_output=True)
    result = VideoQualityChecker().check(str(video), require_audio=True)
    assert result.passed
    assert result.duration_seconds is not None
    assert result.width == 160
    assert result.height == 120
    assert result.has_audio

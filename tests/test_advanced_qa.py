import shutil
import subprocess

import pytest

from app.services.qa.advanced_video_qa import AdvancedVideoQA


def test_advanced_qa_missing_file():
    result = AdvancedVideoQA().check("/missing.mp4")
    assert not result.passed
    assert "video file not found" in result.errors


def test_advanced_qa_real_short_video(tmp_path):
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("FFmpeg/FFprobe not installed")

    path = tmp_path / "qa.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=blue:s=160x120:d=1.2",
            "-f", "lavfi", "-i", "sine=frequency=1000:duration=1.2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(path),
        ],
        check=True, capture_output=True,
    )
    result = AdvancedVideoQA().check(str(path), require_audio=True)
    assert result.passed
    assert result.has_audio
    assert result.duration_seconds is not None
    assert result.errors == []

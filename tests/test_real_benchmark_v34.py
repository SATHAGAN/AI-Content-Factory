from pathlib import Path

from app.services.real_benchmark.config import VideoBenchmarkConfig
from app.services.real_benchmark.runner import validate_video_artifact


def test_benchmark_defaults_are_short():
    config=VideoBenchmarkConfig()
    assert config.frames/config.fps <= 5
    assert config.width <= 512
    assert config.height <= 512


def test_artifact_validator_rejects_missing_file(tmp_path):
    result=validate_video_artifact(str(tmp_path/"missing.mp4"))
    assert result["valid"] is False


def test_artifact_validator_accepts_nonempty_file(tmp_path):
    path=tmp_path/"video.mp4"
    path.write_bytes(b"fake-video")
    result=validate_video_artifact(str(path))
    assert result["valid"] is True
    assert result["size_bytes"]==10

import shutil
import subprocess

import pytest

from app.services.render.pipeline import ProductionRenderPipeline


def test_render_pipeline_real_ffmpeg(tmp_path):
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("FFmpeg/ffprobe not installed")

    scene1 = tmp_path / "scene1.mp4"
    scene2 = tmp_path / "scene2.mp4"

    for path, color in [(scene1, "black"), (scene2, "white")]:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                f"color=c={color}:s=160x120:d=0.5",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)
            ],
            check=True, capture_output=True
        )

    output = tmp_path / "final.mp4"
    result = ProductionRenderPipeline().render([str(scene1), str(scene2)], str(output))
    assert output.exists()
    assert result.qa["passed"]
    assert result.qa["duration_seconds"] > 0

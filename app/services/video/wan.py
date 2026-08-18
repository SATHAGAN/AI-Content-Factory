from __future__ import annotations
import os
import subprocess
from pathlib import Path
from app.services.video.interfaces import VideoGenerationRequest, VideoGenerationResult


class WanVideoGenerator:
    """Adapter for a separately deployed Wan inference worker.

    The worker endpoint is intentionally not called from the API process.
    A production deployment should expose this adapter behind a queue.
    """

    def __init__(self, command: str | None = None, output_dir: str = "./data/generated_video"):
        self.command = command or os.getenv("WAN_GENERATE_COMMAND", "")
        self.output_dir = Path(output_dir)

    def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        if not self.command:
            raise RuntimeError("WAN_GENERATE_COMMAND is not configured")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output = self.output_dir / "scene.mp4"
        command = self.command.format(
            prompt=request.prompt.replace('"', '\\"'),
            output=str(output),
            width=request.width,
            height=request.height,
            frames=request.frames,
            fps=request.fps,
            seed="" if request.seed is None else request.seed,
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=1800)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Video inference failed")
        if not output.exists():
            raise RuntimeError("Video worker completed without producing an output artifact")

        return VideoGenerationResult(
            provider="wan",
            model_id=os.getenv("WAN_MODEL_ID", "Wan-AI/Wan2.1-T2V-1.3B"),
            video_path=str(output),
            duration_seconds=request.frames / request.fps,
        )

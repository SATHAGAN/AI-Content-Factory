from __future__ import annotations

from pathlib import Path

from app.services.video.interface import VideoProviderBackend
from app.services.video.models import (
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoModelInfo,
)


class MockVideoProvider(VideoProviderBackend):
    def __init__(self, output_root: str = "artifacts/video"):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def list_models(self) -> list[VideoModelInfo]:
        return [
            VideoModelInfo(
                model_id="mock-video-v1",
                provider="mock",
                display_name="Mock Video Generator",
                min_vram_gb=0,
                max_duration_seconds=60,
            )
        ]

    def generate(self, request, output_path: str | None = None):
        # Accept both the new duration-based request and the historical
        # frame-based request used by earlier scene workers.
        duration = getattr(request, "duration_seconds", None)
        if duration is None:
            frames = max(1, int(getattr(request, "frames", 1)))
            fps = max(1, int(getattr(request, "fps", 16)))
            duration = frames / fps

        if not self.supports(
            VideoGenerationRequest(
                job_id=getattr(request, "job_id", "legacy-job"),
                prompt=request.prompt,
                duration_seconds=float(duration),
                width=request.width,
                height=request.height,
                fps=request.fps,
                frames=getattr(request, "frames", None),
                seed=request.seed,
                model=getattr(request, "model", None),
                negative_prompt=getattr(request, "negative_prompt", None),
            )
        ):
            raise ValueError("Video request is unsupported by the selected mock model")

        output = (
            Path(output_path)
            if output_path
            else self.output_root / getattr(request, "job_id", "legacy-job") / "video.mp4"
        )
        output.parent.mkdir(parents=True, exist_ok=True)

        output.write_bytes(
            (
                f"MOCK_VIDEO\nprompt={request.prompt}\n"
                f"duration={duration}\nsize={request.width}x{request.height}\n"
                f"fps={request.fps}\n"
            ).encode("utf-8")
        )

        result = VideoGenerationResult(
            job_id=getattr(request, "job_id", "legacy-job"),
            provider="mock",
            model=getattr(request, "model", None) or "mock-video-v1",
            output_path=str(output),
            duration_seconds=float(duration),
            width=request.width,
            height=request.height,
            fps=request.fps,
            metadata={"mock": True},
        )
        return result


# Backward-compatible concrete class name used by earlier media-generation modules.
class MockVideoGenerator(MockVideoProvider):
    pass

from __future__ import annotations

import os
from pathlib import Path

from app.services.providers.contracts import Scene, VideoArtifact


class WanDiffusersProvider:
    """Optional Hugging Face Diffusers adapter for Wan text-to-video.

    This module imports heavy ML dependencies lazily so the web API can run
    without a GPU. A real generation attempt fails with an actionable error
    if CUDA/diffusers/model weights are unavailable.
    """

    provider = "huggingface_diffusers"

    def __init__(self, model_id: str | None = None, device: str | None = None):
        self.model_id = model_id or os.getenv(
            "VIDEO_MODEL_ID", "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
        )
        self.device = device or os.getenv("VIDEO_DEVICE", "cuda")

    def generate(self, scene: Scene, output_dir: str) -> VideoArtifact:
        try:
            import torch
            from diffusers import WanPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Wan provider requires torch and diffusers. Install the optional "
                "video dependencies before enabling this provider."
            ) from exc

        if self.device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError(
                "Wan GPU generation was requested but CUDA is unavailable. "
                "Use a CUDA GPU worker or select VIDEO_PROVIDER=mock."
            )

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        pipe = WanPipeline.from_pretrained(self.model_id, torch_dtype=torch.bfloat16)
        pipe.to(self.device)

        frames = pipe(
            prompt=scene.prompt,
            negative_prompt=scene.negative_prompt or None,
        ).frames[0]

        output_path = Path(output_dir) / f"{scene.scene_id}.mp4"
        from diffusers.utils import export_to_video
        export_to_video(frames, str(output_path), fps=16)

        return VideoArtifact(
            uri=str(output_path),
            duration_seconds=scene.duration_seconds,
            provider=self.provider,
            model_id=self.model_id,
        )

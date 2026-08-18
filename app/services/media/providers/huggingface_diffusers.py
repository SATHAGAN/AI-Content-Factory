from __future__ import annotations

import os
from pathlib import Path


class DiffusersVideoProvider:
    """Optional local Hugging Face Diffusers video backend.

    Heavy model imports happen only when generate() is called, keeping the web
    application lightweight when inference is remote or disabled.
    """

    provider="huggingface-diffusers"

    def __init__(self, model_id: str | None = None):
        self.model_id=model_id or os.getenv("VIDEO_MODEL_ID","Wan-AI/Wan2.1-T2V-1.3B-Diffusers")

    def generate(self, request, output_path: str) -> dict:
        try:
            import torch
            from diffusers import DiffusionPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Install torch and diffusers to use the local Diffusers video provider"
            ) from exc

        output=Path(output_path)
        output.parent.mkdir(parents=True,exist_ok=True)

        dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        pipe=DiffusionPipeline.from_pretrained(self.model_id, torch_dtype=dtype)
        if torch.cuda.is_available():
            pipe=pipe.to("cuda")
        else:
            pipe=pipe.to("cpu")

        frames=max(1,int(request.frames))
        result=pipe(
            prompt=request.prompt,
            num_frames=frames,
            height=int(request.height),
            width=int(request.width),
        )

        frames_data=getattr(result,"frames",None)
        if frames_data is None:
            raise RuntimeError("Video pipeline returned no frames")

        # Export is intentionally delegated to the installed Diffusers/imageio
        # stack. Exact encoding varies by pipeline version.
        try:
            from diffusers.utils import export_to_video
            export_to_video(frames_data[0], str(output), fps=int(request.fps))
        except Exception as exc:
            raise RuntimeError(
                "Diffusers generated frames but video export failed"
            ) from exc

        return {
            "video_path":str(output),
            "duration_seconds":frames / int(request.fps),
            "provider":self.provider,
            "model_id":self.model_id,
        }

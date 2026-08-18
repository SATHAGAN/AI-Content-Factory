from __future__ import annotations

from pathlib import Path


class DiffusersVideoProvider:
    """Optional real video provider.

    Dependencies are imported lazily so the main application remains
    installable on machines without a GPU.
    """

    def __init__(self, model_id: str, device: str = "cuda", dtype: str = "float16"):
        self.model_id=model_id
        self.device=device
        self.dtype=dtype
        self._pipeline=None

    def load(self):
        try:
            import torch
            from diffusers import AutoencoderKLWan, WanPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Install torch and diffusers in the GPU worker environment"
            ) from exc

        if not torch.cuda.is_available() and self.device.startswith("cuda"):
            raise RuntimeError("CUDA GPU is not available")

        dtype=getattr(torch,self.dtype)
        vae=AutoencoderKLWan.from_pretrained(
            self.model_id,
            subfolder="vae",
            torch_dtype=dtype,
        )
        self._pipeline=WanPipeline.from_pretrained(
            self.model_id,
            vae=vae,
            torch_dtype=dtype,
        )
        self._pipeline.to(self.device)
        return self

    def generate(self, *, prompt: str, width: int, height: int, frames: int, fps: int, output_path: str):
        if self._pipeline is None:
            self.load()

        result=self._pipeline(
            prompt=prompt,
            height=height,
            width=width,
            num_frames=frames,
            guidance_scale=5.0,
        )
        video=result.frames[0]
        output=Path(output_path)
        output.parent.mkdir(parents=True,exist_ok=True)

        try:
            from diffusers.utils import export_to_video
        except ImportError as exc:
            raise RuntimeError("diffusers video export utilities are unavailable") from exc

        export_to_video(video,str(output),fps=fps)
        return str(output)


class QwenTTSProvider:
    """Optional real Qwen3-TTS provider boundary.

    The exact checkpoint and runtime API are intentionally configurable because
    Qwen3-TTS checkpoints/runtime interfaces can evolve.
    """

    def __init__(self, model_id: str, device: str = "cuda"):
        self.model_id=model_id
        self.device=device

    def generate(self, *, text: str, language: str, output_path: str):
        raise NotImplementedError(
            "Connect the pinned Qwen3-TTS checkpoint/runtime here after "
            "selecting the exact deployment checkpoint."
        )

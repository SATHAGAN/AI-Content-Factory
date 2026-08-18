from __future__ import annotations

from pathlib import Path

from app.services.audio.models import TTSRequest


class Qwen3TTSProvider:
    """Real Qwen3-TTS adapter boundary.

    The model is loaded lazily on the GPU worker. The exact checkpoint is
    supplied by the selected TTSProfile.
    """

    def __init__(self, model_id: str, device: str = "cuda"):
        self.model_id=model_id
        self.device=device
        self.model=None

    def load(self):
        try:
            import torch
            from qwen_tts import Qwen3TTSModel
        except ImportError as exc:
            raise RuntimeError(
                "Install qwen-tts and its GPU dependencies on the inference worker"
            ) from exc

        if self.device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU is not available")

        self.model=Qwen3TTSModel.from_pretrained(
            self.model_id,
            device_map=self.device,
            dtype=torch.bfloat16,
            attn_implementation="sdpa",
        )
        return self

    def generate(self, request: TTSRequest, *, speaker: str | None = None):
        if self.model is None:
            self.load()

        output=Path(request.output_path)
        output.parent.mkdir(parents=True,exist_ok=True)

        kwargs={
            "text":request.text,
            "language":request.language,
        }
        if speaker:
            kwargs["speaker"]=speaker

        # Qwen3-TTS exposes inference through the qwen_tts package.
        # Keep the call isolated here so provider/runtime changes do not
        # affect the rest of the application.
        wavs, sr=self.model.generate_custom_voice(**kwargs)
        import soundfile as sf
        sf.write(str(output),wavs[0],sr)
        return str(output)

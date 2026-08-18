from __future__ import annotations

import os
from pathlib import Path

from app.services.providers.contracts import AudioArtifact


class Qwen3TTSProvider:
    """Optional Qwen3-TTS adapter.

    The heavy qwen-tts dependency is imported only when this provider is used.
    """

    provider = "qwen3_tts"

    def __init__(self, model_id: str | None = None, device: str | None = None):
        self.model_id = model_id or os.getenv(
            "TTS_MODEL_ID", "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
        )
        self.device = device or os.getenv("TTS_DEVICE", "cuda")

    def synthesize(self, text: str, output_dir: str, voice: str | None = None) -> AudioArtifact:
        try:
            import torch
            import soundfile as sf
            from qwen_tts import Qwen3TTSModel
        except ImportError as exc:
            raise RuntimeError(
                "Qwen3-TTS requires qwen-tts, torch and soundfile. "
                "Install the optional TTS dependencies before enabling this provider."
            ) from exc

        if self.device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError(
                "Qwen3-TTS GPU generation was requested but CUDA is unavailable."
            )

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        model = Qwen3TTSModel.from_pretrained(
            self.model_id,
            device_map=self.device,
            dtype=torch.bfloat16 if self.device.startswith("cuda") else torch.float32,
        )

        speaker = voice or "Ryan"
        wavs, sample_rate = model.generate_custom_voice(
            text=text,
            language="English",
            speaker=speaker,
            instruct="Speak clearly and naturally for a video narration.",
        )

        output_path = Path(output_dir) / "narration.wav"
        sf.write(str(output_path), wavs[0], sample_rate)

        # Exact duration is deferred to FFprobe in the media layer.
        return AudioArtifact(
            str(output_path),
            0.0,
            self.provider,
            self.model_id,
            {"speaker": speaker, "sample_rate": sample_rate},
        )

from __future__ import annotations

from dataclasses import dataclass

from app.services.tts.interface import TTSProviderBackend
from app.services.tts.models import TTSModelInfo, TTSRequest


@dataclass(frozen=True)
class TTSWorkerProfile:
    worker_id: str
    vram_gb: float
    providers: tuple[str, ...] = ()


class TTSModelSelector:
    def __init__(
        self,
        providers: list[TTSProviderBackend],
        worker_profile: TTSWorkerProfile | None = None,
    ):
        self.providers = providers
        self.worker_profile = worker_profile

    def available_models(self) -> list[TTSModelInfo]:
        models = [m for p in self.providers for m in p.list_models() if m.enabled]
        if self.worker_profile is None:
            return models
        return [
            m for m in models
            if m.min_vram_gb <= self.worker_profile.vram_gb
            and (
                not self.worker_profile.providers
                or m.provider in self.worker_profile.providers
            )
        ]

    def select(self, request: TTSRequest) -> TTSModelInfo:
        candidates = [
            m for m in self.available_models()
            if request.language in m.languages
            and request.voice in m.voices
            and len(request.text) <= m.max_text_characters
            and (request.model is None or request.model == m.model_id)
        ]
        if not candidates:
            raise ValueError(
                "No compatible TTS model for "
                f"language={request.language!r}, voice={request.voice!r}, "
                f"model={request.model!r}"
            )
        return sorted(candidates, key=lambda m: (m.min_vram_gb, m.model_id))[0]

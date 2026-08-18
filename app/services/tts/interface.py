from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.tts.models import TTSModelInfo, TTSRequest, TTSResult


class TTSProviderBackend(ABC):
    @abstractmethod
    def list_models(self) -> list[TTSModelInfo]:
        raise NotImplementedError

    @abstractmethod
    def synthesize(self, request: TTSRequest) -> TTSResult:
        raise NotImplementedError

    def supports(self, request: TTSRequest) -> bool:
        return any(
            model.enabled
            and request.language in model.languages
            and request.voice in model.voices
            and len(request.text) <= model.max_text_characters
            and (getattr(request, "model", None) is None
                 or getattr(request, "model", None) == model.model_id)
            for model in self.list_models()
        )

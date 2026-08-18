from __future__ import annotations

from app.services.tts.interface import TTSProviderBackend
from app.services.tts.models import TTSRequest, TTSResult
from app.services.tts.selector import TTSModelSelector


class TTSGenerationService:
    def __init__(
        self,
        providers: list[TTSProviderBackend],
        selector: TTSModelSelector | None = None,
    ):
        self.providers = providers
        self.selector = selector or TTSModelSelector(providers)

    def synthesize(self, request: TTSRequest) -> TTSResult:
        model = self.selector.select(request)
        for provider in self.providers:
            if any(m.model_id == model.model_id for m in provider.list_models()):
                effective = request
                if effective.model is None:
                    effective = TTSRequest(
                        **{**effective.__dict__, "model": model.model_id}
                    )
                return provider.synthesize(effective)
        raise RuntimeError(f"Selected TTS model provider disappeared: {model.model_id}")

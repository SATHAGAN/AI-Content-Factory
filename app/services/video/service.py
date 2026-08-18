from __future__ import annotations

from app.services.video.interface import VideoProviderBackend
from app.services.video.models import VideoGenerationRequest, VideoGenerationResult
from app.services.video.selector import VideoModelSelector


class VideoGenerationService:
    def __init__(
        self,
        providers: list[VideoProviderBackend],
        selector: VideoModelSelector | None = None,
    ):
        self.providers = providers
        self.selector = selector or VideoModelSelector(providers)

    def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        model = self.selector.select(request)

        for provider in self.providers:
            if any(m.model_id == model.model_id for m in provider.list_models()):
                effective = request
                if effective.model is None:
                    effective = VideoGenerationRequest(
                        **{**effective.__dict__, "model": model.model_id}
                    )
                return provider.generate(effective)

        raise RuntimeError(f"Selected model provider disappeared: {model.model_id}")

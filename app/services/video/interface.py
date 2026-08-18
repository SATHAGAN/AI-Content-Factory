from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.video.models import (
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoModelInfo,
)


class VideoProviderBackend(ABC):
    @abstractmethod
    def list_models(self) -> list[VideoModelInfo]:
        raise NotImplementedError

    @abstractmethod
    def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        raise NotImplementedError

    def supports(self, request: VideoGenerationRequest) -> bool:
        return any(
            model.enabled
            and model.supports_text_to_video
            and request.duration_seconds <= model.max_duration_seconds
            and (request.model is None or request.model == model.model_id)
            for model in self.list_models()
        )

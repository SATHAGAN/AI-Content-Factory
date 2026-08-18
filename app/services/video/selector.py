from __future__ import annotations

from dataclasses import dataclass

from app.services.video.interface import VideoProviderBackend
from app.services.video.models import VideoGenerationRequest, VideoModelInfo


@dataclass(frozen=True)
class WorkerVideoProfile:
    worker_id: str
    vram_gb: float
    providers: tuple[str, ...] = ()


class VideoModelSelector:
    """Chooses a compatible model without hard-coding a specific AI vendor."""

    def __init__(
        self,
        providers: list[VideoProviderBackend],
        worker_profile: WorkerVideoProfile | None = None,
    ):
        self.providers = providers
        self.worker_profile = worker_profile

    def available_models(self) -> list[VideoModelInfo]:
        models = []
        for provider in self.providers:
            models.extend(provider.list_models())

        if self.worker_profile is None:
            return [m for m in models if m.enabled]

        return [
            m for m in models
            if m.enabled
            and m.min_vram_gb <= self.worker_profile.vram_gb
            and (
                not self.worker_profile.providers
                or m.provider in self.worker_profile.providers
            )
        ]

    def select(self, request: VideoGenerationRequest) -> VideoModelInfo:
        candidates = self.available_models()

        if request.model:
            candidates = [m for m in candidates if m.model_id == request.model]

        candidates = [
            m for m in candidates
            if m.supports_text_to_video
            and request.duration_seconds <= m.max_duration_seconds
        ]

        if not candidates:
            raise ValueError(
                "No compatible video model for "
                f"duration={request.duration_seconds}, model={request.model!r}"
            )

        # Prefer the smallest capable model to avoid wasting GPU memory.
        return sorted(candidates, key=lambda m: (m.min_vram_gb, m.model_id))[0]

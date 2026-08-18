from __future__ import annotations

from app.services.model_catalog.models import ModelSpec


class ModelSelector:
    def select(
        self,
        candidates: list[ModelSpec],
        *,
        gpu_vram_gb: int | None,
        prefer_local: bool = False,
    ) -> ModelSpec:
        compatible=[
            m for m in candidates
            if m.min_gpu_vram_gb is None
            or gpu_vram_gb is None
            or gpu_vram_gb >= m.min_gpu_vram_gb
        ]
        if not compatible:
            raise RuntimeError("No compatible model found for the supplied hardware")

        if prefer_local:
            local=[m for m in compatible if not m.remote_recommended]
            if local:
                return local[0]

        return sorted(
            compatible,
            key=lambda m:(m.remote_recommended, m.min_gpu_vram_gb or 0),
        )[0]

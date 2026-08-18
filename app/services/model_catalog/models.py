from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    provider: str
    task: str
    license: str = ""
    min_gpu_vram_gb: int | None = None
    remote_recommended: bool = False
    notes: str = ""
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class V1ModelProfile:
    llm: ModelSpec
    video: ModelSpec
    tts: ModelSpec
    qa: ModelSpec
    embedding: ModelSpec | None = None
    extra: dict = field(default_factory=dict)

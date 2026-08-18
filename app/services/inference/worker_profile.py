from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GPUWorkerProfile:
    worker_id: str
    gpu_name: str
    vram_gb: float
    cuda_version: str | None = None
    inference_backend: str = "pytorch"
    enabled_tasks: tuple[str, ...] = ("llm","video","tts","qa")


def supports(profile: GPUWorkerProfile, *, task: str, required_vram_gb: float | None):
    if task not in profile.enabled_tasks:
        return False
    if required_vram_gb is not None and profile.vram_gb < required_vram_gb:
        return False
    return True

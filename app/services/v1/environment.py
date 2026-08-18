from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeEnvironment:
    name: str
    gpu_vram_gb: int | None
    inference_location: str
    storage_provider: str
    scheduler_enabled: bool


def classify_environment(env: RuntimeEnvironment) -> dict:
    local_video_possible=(
        env.gpu_vram_gb is not None and env.gpu_vram_gb >= 8
    )
    return {
        "environment":env.name,
        "local_video_possible":local_video_possible,
        "inference_location":env.inference_location,
        "storage_provider":env.storage_provider,
        "scheduler_enabled":env.scheduler_enabled,
        "recommendation":(
            "remote_gpu"
            if not local_video_possible
            else "local_or_remote_gpu"
        ),
    }

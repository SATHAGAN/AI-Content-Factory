from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VideoProvider(str, Enum):
    MOCK = "mock"
    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True)
class VideoGenerationRequest:
    job_id: str = "legacy-job"
    prompt: str = ""
    duration_seconds: float = 0.0
    width: int = 1280
    height: int = 720
    fps: int = 24
    frames: int | None = None
    seed: int | None = None
    model: str | None = None
    negative_prompt: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class VideoGenerationResult:
    job_id: str
    provider: str
    model: str
    output_path: str
    duration_seconds: float
    width: int
    height: int
    fps: int
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class VideoModelInfo:
    model_id: str
    provider: str
    display_name: str
    min_vram_gb: float
    max_duration_seconds: float
    supports_text_to_video: bool = True
    supports_image_to_video: bool = False
    enabled: bool = True
    metadata: dict = field(default_factory=dict)


# Compatibility aliases used by the pre-Phase-48 media layer.
def _result_video_path(self):
    return self.output_path

def _result_model_id(self):
    return self.model

VideoGenerationResult.video_path = property(_result_video_path)
VideoGenerationResult.model_id = property(_result_model_id)

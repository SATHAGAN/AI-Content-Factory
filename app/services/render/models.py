from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RenderStatus(str, Enum):
    READY = "ready"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


@dataclass(frozen=True)
class SceneArtifact:
    scene_id: str
    video_path: str
    duration_seconds: float
    order: int
    audio_path: str | None = None
    subtitle_path: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RenderConfig:
    output_path: str
    add_voiceover: bool = True
    add_subtitles: bool = False
    add_background_music: bool = False
    background_music_path: str | None = None
    music_volume: float = 0.12
    normalize_audio: bool = True
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "medium"
    crf: int = 20


@dataclass(frozen=True)
class RenderManifest:
    scenes: tuple[SceneArtifact, ...]
    total_duration_seconds: float
    output_path: str
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RenderResult:
    status: RenderStatus
    output_path: str
    duration_seconds: float
    command: tuple[str, ...] = ()
    message: str = ""
    metadata: dict = field(default_factory=dict)

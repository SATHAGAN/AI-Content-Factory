from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Scene:
    scene_id: str
    prompt: str
    narration: str
    duration_seconds: float
    negative_prompt: str = ""


@dataclass(frozen=True)
class VideoArtifact:
    uri: str
    duration_seconds: float
    provider: str
    model_id: str
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class AudioArtifact:
    uri: str
    duration_seconds: float
    provider: str
    model_id: str
    metadata: dict = field(default_factory=dict)


class VideoProvider(Protocol):
    def generate(self, scene: Scene, output_dir: str) -> VideoArtifact: ...


class TTSProvider(Protocol):
    def synthesize(self, text: str, output_dir: str, voice: str | None = None) -> AudioArtifact: ...


class LLMProvider(Protocol):
    def plan(self, source_text: str, target_duration_seconds: int, category: str) -> list[Scene]: ...

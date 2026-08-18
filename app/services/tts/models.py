from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TTSProvider(str, Enum):
    MOCK = "mock"
    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True)
class TTSRequest:
    text: str
    language: str = "en"
    voice: str = "default"
    speed: float = 1.0
    pitch: float = 0.0
    sample_rate: int = 24000
    model: str | None = None
    job_id: str = "legacy-job"
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class TTSResult:
    provider: str
    model: str
    audio_path: str
    duration_seconds: float
    sample_rate: int
    language: str
    voice: str
    metadata: dict = field(default_factory=dict)

    @property
    def path(self) -> str:
        return self.audio_path

    @property
    def model_id(self) -> str:
        return self.model


@dataclass(frozen=True)
class TTSModelInfo:
    model_id: str
    provider: str
    display_name: str
    min_vram_gb: float
    max_text_characters: int
    languages: tuple[str, ...] = ("en",)
    voices: tuple[str, ...] = ("default",)
    enabled: bool = True
    supports_streaming: bool = False
    metadata: dict = field(default_factory=dict)

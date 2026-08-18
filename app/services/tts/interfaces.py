from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class TTSRequest:
    text: str
    language: str = "en"
    voice: str = "default"
    speed: float = 1.0

@dataclass(frozen=True)
class TTSResult:
    provider: str
    model_id: str
    audio_path: str
    duration_seconds: float

class TTSProvider(Protocol):
    def synthesize(self, request: TTSRequest, output_path: str | None = None) -> TTSResult:
        ...

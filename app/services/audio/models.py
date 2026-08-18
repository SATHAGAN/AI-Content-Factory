from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class TTSRequest:
    text: str
    language: str = "English"
    voice: str | None = None
    output_path: str = "./benchmark_output/voice.wav"
    sample_rate: int = 24000


@dataclass(frozen=True)
class AudioMetadata:
    path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    size_bytes: int

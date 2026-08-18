from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class STTConfig:
    provider: str = "local"
    model: str = "auto"
    language: str | None = None
    word_timestamps: bool = True
    vad_filter: bool = True
    temperature: float = 0.0


@dataclass(frozen=True)
class STTWord:
    text: str
    start_seconds: float
    end_seconds: float
    confidence: float | None = None


@dataclass(frozen=True)
class STTSegment:
    text: str
    start_seconds: float
    end_seconds: float
    words: tuple[STTWord, ...] = ()


@dataclass(frozen=True)
class STTResult:
    text: str
    language: str | None
    duration_seconds: float | None
    segments: tuple[STTSegment, ...]
    words: tuple[STTWord, ...]
    provider: str
    model: str
    metadata: dict = field(default_factory=dict)

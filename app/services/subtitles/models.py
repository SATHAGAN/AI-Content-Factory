from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SubtitleFormat(str, Enum):
    SRT = "srt"
    VTT = "vtt"


@dataclass(frozen=True)
class TranscriptWord:
    text: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True)
class SubtitleSegment:
    index: int
    text: str
    start_seconds: float
    end_seconds: float
    words: tuple[TranscriptWord, ...] = ()


@dataclass(frozen=True)
class SubtitleConfig:
    format: SubtitleFormat = SubtitleFormat.SRT
    max_chars_per_line: int = 42
    max_lines: int = 2
    max_duration_seconds: float = 4.0
    min_duration_seconds: float = 0.8
    include_word_timestamps: bool = False


@dataclass(frozen=True)
class SubtitleArtifact:
    path: str
    format: SubtitleFormat
    segment_count: int
    duration_seconds: float
    metadata: dict = field(default_factory=dict)

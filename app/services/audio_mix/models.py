from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AudioMixMode(str, Enum):
    VOICE_PRIORITY = "voice_priority"
    BALANCED = "balanced"
    MUSIC_ONLY = "music_only"


@dataclass(frozen=True)
class AudioMixConfig:
    voice_volume: float = 1.0
    music_volume: float = 0.12
    music_ducking: bool = True
    ducked_music_volume: float = 0.06
    mode: AudioMixMode = AudioMixMode.VOICE_PRIORITY
    normalize_voice: bool = True
    normalize_music: bool = True
    sample_rate: int = 48000


@dataclass(frozen=True)
class AudioMixRequest:
    video_path: str
    voice_path: str | None
    music_path: str | None
    output_path: str
    config: AudioMixConfig = AudioMixConfig()


@dataclass(frozen=True)
class AudioMixResult:
    output_path: str
    command: tuple[str, ...]
    voice_enabled: bool
    music_enabled: bool
    metadata: dict


from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Platform(str,Enum):
    YOUTUBE="youtube"
    INSTAGRAM="instagram"


@dataclass(frozen=True)
class VoiceConfig:
    profile_id: str
    language: str = "English"
    speaker: str | None = None
    speed: float = 1.0


@dataclass(frozen=True)
class ChannelConfig:
    channel_id: str
    name: str
    category: str
    language: str
    audience: str
    tone: str
    default_duration_seconds: float
    platforms: tuple[Platform,...]
    voice: VoiceConfig
    enabled: bool = True
    schedule: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


# Backward-compatible configuration used by the existing publishing/orchestration
# layer from earlier phases.
@dataclass
class ChannelProfile:
    channel_id: str
    name: str
    categories: list[str]
    languages: list[str]
    platforms: list[str]
    daily_quota: dict[str,int]
    enabled: bool = True
    brand_profile: dict = field(default_factory=dict)
    default_models: dict = field(default_factory=dict)

    def __post_init__(self):
        self.platforms=[p.value if isinstance(p,Platform) else str(p) for p in self.platforms]


@dataclass(frozen=True)
class ChannelPlatformAccount:
    channel_id: str
    platform: str
    account_key: str


@dataclass(frozen=True)
class ChannelJob:
    job_id: str
    channel_id: str
    content_source_id: str
    target_platforms: tuple[Platform,...]
    duration_seconds: float | None = None
    metadata: dict = field(default_factory=dict)

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SceneClip:
    scene_id: str
    video_path: str
    duration_seconds: float
    audio_path: str | None = None
    subtitle_path: str | None = None
    title: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Timeline:
    clips: tuple[SceneClip, ...]
    total_duration_seconds: float

    @property
    def scene_count(self) -> int:
        return len(self.clips)

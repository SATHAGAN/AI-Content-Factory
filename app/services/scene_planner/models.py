from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SceneSpec:
    scene_id: str
    sequence: int
    narration: str
    visual_prompt: str
    duration_seconds: float
    subtitle_text: str
    camera: str = "static"
    motion: str = "gentle"
    music_mood: str = "neutral"
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class StoryPlan:
    title: str
    hook: str
    language: str
    category: str
    target_duration_seconds: float
    scenes: tuple[SceneSpec, ...]
    metadata: dict = field(default_factory=dict)

    @property
    def total_scene_duration(self) -> float:
        return sum(scene.duration_seconds for scene in self.scenes)

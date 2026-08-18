from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Character(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=1000)
    visual_traits: list[str] = Field(default_factory=list)
    voice_traits: list[str] = Field(default_factory=list)


class ScenePlan(BaseModel):
    scene_id: str
    order: int = Field(ge=1)
    duration_seconds: float = Field(gt=0, le=120)
    visual_prompt: str = Field(min_length=1, max_length=4000)
    narration: str = Field(min_length=1, max_length=5000)
    dialogue: list[str] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    transition: str = "cut"
    continuity_notes: list[str] = Field(default_factory=list)


class ContentPlan(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    hook: str = Field(min_length=1, max_length=1000)
    category: str = Field(min_length=1, max_length=80)
    language: str = Field(min_length=1, max_length=80)
    target_duration_seconds: int = Field(ge=15, le=3600)
    tone: str = Field(min_length=1, max_length=80)
    audience: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=3000)
    characters: list[Character] = Field(default_factory=list)
    scenes: list[ScenePlan] = Field(min_length=1)
    keywords: list[str] = Field(default_factory=list)

    @field_validator("scenes")
    @classmethod
    def validate_scene_order(cls, scenes):
        orders=[s.order for s in scenes]
        if orders != list(range(1,len(scenes)+1)):
            raise ValueError("Scene order must be contiguous starting at 1")
        return scenes

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    source_text: str = Field(min_length=1, max_length=100_000)
    content_category: str = Field(default="general", min_length=1, max_length=100)
    language: str = Field(default="en", min_length=2, max_length=32)
    audience: str = Field(default="general audience", min_length=1, max_length=160)
    tone: str = Field(default="engaging", min_length=1, max_length=100)
    duration_seconds: int = Field(default=60, ge=15, le=3600)
    video_type: str = Field(default="short", min_length=1, max_length=50)


class SceneResponse(BaseModel):
    number: int
    duration_seconds: int
    purpose: str
    visual_prompt: str
    narration: str
    dialogue: list[str]
    sound_effects: list[str]
    transition: str


class ContentPlanResponse(BaseModel):
    title: str
    hook: str
    summary: str
    audience: str
    language: str
    tone: str
    characters: list[dict]
    style_bible: dict
    scenes: list[SceneResponse]

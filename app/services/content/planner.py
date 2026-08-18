from __future__ import annotations

import re
from app.services.content.schemas import Character, ContentPlan, ScenePlan
from pydantic import BaseModel, Field


class PlanningRequest(BaseModel):
    source_text: str = Field(min_length=1, max_length=100000)
    category: str = "General"
    content_category: str | None = None
    language: str = "English"
    duration_seconds: int = Field(default=60, ge=15, le=3600)
    tone: str = "Engaging"
    audience: str = "General audience"
    video_type: str = "short"

    @property
    def resolved_category(self) -> str:
        return self.content_category or self.category


CATEGORY_GUIDANCE = {
    "Kids": "Keep language simple, positive, age-appropriate and visually expressive.",
    "Educational": "Explain concepts clearly with concrete examples and accurate wording.",
    "Facts": "Use concise factual narration and avoid unsupported claims.",
    "Motivation": "Use an encouraging structure with a clear practical takeaway.",
    "Creative": "Prioritize originality, visual imagination and emotional progression.",
    "General": "Use an engaging, broadly accessible storytelling structure.",
}


class ContentPlanner:
    def __init__(self, provider=None):
        # `provider` preserves the earlier AI factory contract. The structured
        # V1 planner remains deterministic unless an explicit generator is used.
        self.provider = provider
    """Deterministic planner for V1.

    The output contract is intentionally the same contract a real LLM adapter
    will populate later. This lets downstream video/TTS code develop now.
    """

    def plan(
        self,
        source_text: str | PlanningRequest,
        *,
        category: str | None = None,
        language: str | None = None,
        duration_seconds: int | None = None,
        tone: str | None = None,
        audience: str | None = None,
    ) -> ContentPlan:
        # Backward-compatible support for the original PlanningRequest API.
        if isinstance(source_text, PlanningRequest):
            request = source_text
            source_text = request.source_text
            category = request.resolved_category
            language = request.language
            duration_seconds = request.duration_seconds
            tone = request.tone
            audience = request.audience
        category = category or "General"
        language = language or "English"
        duration_seconds = duration_seconds or 60
        tone = tone or "Engaging"
        audience = audience or "General audience"
        text = " ".join(source_text.split())
        if not text:
            raise ValueError("source_text cannot be empty")

        # Split on sentence boundaries and keep a bounded amount of source context.
        parts=[p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
        if not parts:
            parts=[text[:500]]

        scene_count=max(1,min(20,round(duration_seconds/15)))
        scenes=[]
        per_duration=duration_seconds/scene_count

        for i in range(scene_count):
            seed=parts[i % len(parts)]
            scenes.append(ScenePlan(
                scene_id=f"scene_{i+1:03d}",
                order=i+1,
                duration_seconds=per_duration,
                visual_prompt=(
                    f"{category} scene, {tone} tone, consistent cinematic style. "
                    f"Visualize: {seed}"
                ),
                narration=seed,
                characters=["main_character"] if category=="Kids" else [],
                transition="cut" if i==0 else "crossfade",
                continuity_notes=["Keep character appearance and visual style consistent."],
            ))

        characters=[]
        if category=="Kids":
            characters=[Character(
                id="main_character",
                name="Main Character",
                description="Friendly, expressive child-safe story character.",
                visual_traits=["consistent outfit","expressive face","soft cinematic lighting"],
                voice_traits=["warm","clear","friendly"],
            )]

        title_seed=parts[0][:70].rstrip(".!?")
        title=title_seed if title_seed else f"{category} Story"
        return ContentPlan(
            title=title,
            hook=parts[0][:250],
            category=category,
            language=language,
            target_duration_seconds=duration_seconds,
            tone=tone,
            audience=audience,
            summary=text[:2000],
            characters=characters,
            scenes=scenes,
            keywords=[category.lower(), tone.lower()],
        )

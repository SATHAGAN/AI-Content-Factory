from __future__ import annotations

from app.services.scene_planner.parser import parse_story_plan
from app.services.scene_planner.prompts import SYSTEM_PROMPT,build_user_prompt
from app.services.scene_planner.validator import validate_story_plan


class ScenePlannerService:
    def __init__(self, llm):
        self.llm=llm

    def plan(
        self,
        *,
        source_text: str,
        category: str,
        language: str,
        target_duration_seconds: float,
        scene_duration_seconds: float = 8.0,
        audience: str = "general",
        tone: str = "engaging",
    ):
        prompt=build_user_prompt(
            source_text=source_text,
            category=category,
            language=language,
            target_duration_seconds=target_duration_seconds,
            scene_duration_seconds=scene_duration_seconds,
            audience=audience,
            tone=tone,
        )
        raw=self.llm.generate(
            system=SYSTEM_PROMPT,
            prompt=prompt,
            response_format="json",
        )
        plan=parse_story_plan(raw)
        errors=validate_story_plan(plan)
        if errors:
            raise ValueError("; ".join(errors))
        return plan

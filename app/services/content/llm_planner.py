from __future__ import annotations

import json
from typing import Any

from app.services.content.planner import ContentPlanner
from app.services.content.schemas import ContentPlan


SYSTEM_PROMPT = """You are a structured content planner for an automated video factory.
Return ONLY valid JSON matching the ContentPlan schema.
Never invent factual claims when the source does not support them.
Keep children's content age-appropriate and avoid unsafe or frightening material.
Maintain consistent characters, setting and visual style across scenes.
"""


class LLMContentPlanner:
    """LLM adapter boundary.

    The V1 implementation uses the deterministic planner. A real local or
    hosted model can be connected through `generate_json` without changing
    the ContentPlan schema or downstream pipeline.
    """

    def __init__(self, generator=None):
        self.generator=generator

    def build_prompt(self, source_text: str, category: str, language: str, duration_seconds: int, tone: str, audience: str) -> str:
        return json.dumps({
            "system": SYSTEM_PROMPT,
            "task": "Create a complete video content plan.",
            "source_text": source_text,
            "category": category,
            "language": language,
            "duration_seconds": duration_seconds,
            "tone": tone,
            "audience": audience,
            "requirements": [
                "Create a hook.",
                "Create ordered scenes.",
                "Create visual prompts.",
                "Create narration.",
                "Track recurring characters.",
                "Keep total scene duration equal to the requested duration."
            ],
        }, ensure_ascii=False)

    def plan(self, source_text: str, **kwargs: Any) -> ContentPlan:
        if self.generator is None:
            return ContentPlanner().plan(source_text, **kwargs)

        raw=self.generator(self.build_prompt(source_text, **kwargs))
        if isinstance(raw,str):
            raw=json.loads(raw)
        return ContentPlan.model_validate(raw)

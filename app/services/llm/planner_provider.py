from __future__ import annotations

import json

from app.services.content.planner import ContentPlanner
from app.services.content.schemas import ContentPlan
from app.services.llm.json_contract import parse_structured_output
from app.services.llm.models import LLMConfig
from app.services.llm.openai_compatible import OpenAICompatibleClient


SYSTEM_PROMPT = """You are the planning engine for an automated video content factory.
Return only JSON matching the requested schema.
Do not invent facts not supported by the source.
For children, keep content age-appropriate and safe.
Keep recurring character descriptions consistent across scenes.
Make scene narration and visual prompts directly correspond.
"""


class StructuredLLMPlanner:
    def __init__(self, config: LLMConfig):
        self.config=config
        self.client=OpenAICompatibleClient(config)

    def plan(self, source_text: str, *, category: str, language: str, duration_seconds: int, tone: str, audience: str) -> ContentPlan:
        schema_hint={
            "title":"string",
            "hook":"string",
            "category":category,
            "language":language,
            "target_duration_seconds":duration_seconds,
            "tone":tone,
            "audience":audience,
            "summary":"string",
            "characters":[],
            "scenes":[
                {
                    "scene_id":"scene_001",
                    "order":1,
                    "duration_seconds":15,
                    "visual_prompt":"string",
                    "narration":"string",
                    "dialogue":[],
                    "characters":[],
                    "transition":"cut",
                    "continuity_notes":[]
                }
            ],
            "keywords":[]
        }
        user=f"""Source:
{source_text}

Create a {duration_seconds}-second {category} video in {language}.
Tone: {tone}
Audience: {audience}

Required JSON shape:
{json.dumps(schema_hint,ensure_ascii=False)}
"""
        raw=self.client.text(SYSTEM_PROMPT,user)
        return parse_structured_output(raw,ContentPlan)

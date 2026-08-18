from __future__ import annotations

import json
from typing import Any

from app.services.ai.interfaces import GenerationResult, LLMProvider


class MockLLM(LLMProvider):
    """Deterministic development provider; never calls an external model."""

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        topic = prompt.strip().splitlines()[-1][:120] or "the requested topic"
        payload = {
            "title": "A New Story",
            "hook": f"Discover something surprising about {topic}.",
            "summary": "An original short-form story plan.",
            "audience": "general audience",
            "language": "en",
            "tone": "engaging",
            "characters": [],
            "style_bible": {
                "visual_style": "clean cinematic animation",
                "color_mood": "warm",
                "camera_style": "gentle cinematic",
                "consistency_rules": [],
            },
            "scenes": [
                {
                    "number": 1,
                    "duration_seconds": 8,
                    "purpose": "hook",
                    "visual_prompt": f"Cinematic opening related to {topic}",
                    "narration": "Let us begin.",
                    "dialogue": [],
                    "sound_effects": [],
                    "transition": "cut",
                },
                {
                    "number": 2,
                    "duration_seconds": 8,
                    "purpose": "development",
                    "visual_prompt": f"Main action related to {topic}",
                    "narration": "The story continues.",
                    "dialogue": [],
                    "sound_effects": [],
                    "transition": "dissolve",
                },
                {
                    "number": 3,
                    "duration_seconds": 8,
                    "purpose": "resolution",
                    "visual_prompt": f"Warm closing related to {topic}",
                    "narration": "And that is the lesson.",
                    "dialogue": [],
                    "sound_effects": [],
                    "transition": "fade",
                },
            ],
        }
        return GenerationResult(
            provider="mock",
            model_id="mock-content-planner-v1",
            output={"text": json.dumps(payload)},
        )

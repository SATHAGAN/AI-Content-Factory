from __future__ import annotations

import json
import math
import re
from typing import Any

from app.services.ai.interfaces import GenerationResult, LLMProvider


class MockLLM(LLMProvider):
    """Deterministic development provider; never calls an external model."""

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        lines = prompt.strip().splitlines()
        topic = "the requested topic"
        for index, line in enumerate(lines):
            if line.strip() == "Source/topic:" and index + 1 < len(lines):
                topic = lines[index + 1].strip()[:120] or topic
                break

        match = re.search(r"Target duration:\s*([0-9]+(?:\.[0-9]+)?)\s*seconds", prompt, re.I)
        target_duration = float(match.group(1)) if match else 24.0
        scene_match = re.search(r"Target scene duration:\s*([0-9]+(?:\.[0-9]+)?)\s*seconds", prompt, re.I)
        scene_duration = float(scene_match.group(1)) if scene_match else 8.0
        scene_count = max(1, math.ceil(target_duration / scene_duration))
        base_duration = target_duration / scene_count

        purposes = ["hook", "development", "development", "resolution"]
        scenes = []
        remaining = target_duration
        for index in range(scene_count):
            duration = base_duration if index < scene_count - 1 else remaining
            remaining -= duration
            purpose = purposes[min(index, len(purposes) - 1)]
            scenes.append({
                "scene_id": f"scene-{index + 1}",
                "sequence": index + 1,
                "number": index + 1,
                "duration_seconds": round(duration, 3),
                "purpose": purpose,
                "visual_prompt": f"Cinematic {purpose} scene about {topic}",
                "narration": f"This is scene {index + 1}, explaining {topic}.",
                "subtitle_text": f"This is scene {index + 1}, explaining {topic}.",
                "camera": "gentle cinematic",
                "motion": "subtle movement",
                "music_mood": "warm",
                "dialogue": [],
                "sound_effects": [],
                "transition": "cut" if index == 0 else "dissolve",
            })

        payload = {
            "title": "AI Content Factory Demo",
            "hook": f"Discover something useful about {topic}.",
            "summary": f"A short educational video about {topic}.",
            "audience": "general audience",
            "language": "en",
            "tone": "engaging",
            "category": "education",
            "target_duration_seconds": target_duration,
            "characters": [],
            "style_bible": {
                "visual_style": "clean cinematic animation",
                "color_mood": "warm",
                "camera_style": "gentle cinematic",
                "consistency_rules": [],
            },
            "scenes": scenes,
        }
        return GenerationResult(
            provider="mock",
            model_id="mock-content-planner-v1",
            output={"text": json.dumps(payload)},
        )

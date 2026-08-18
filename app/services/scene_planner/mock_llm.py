from __future__ import annotations

import json
import math


class MockSceneLLM:
    def generate(self, *, system: str, prompt: str, response_format: str):
        target=40.0
        scene_duration=8.0

        # The mock is intentionally deterministic and only exists for tests.
        scenes=[]
        count=math.ceil(target/scene_duration)
        for i in range(1,count+1):
            duration=scene_duration if i<count else target-scene_duration*(count-1)
            scenes.append({
                "scene_id":f"scene-{i:03d}",
                "sequence":i,
                "narration":f"Scene {i} narration for the story.",
                "visual_prompt":(
                    f"Friendly animated story scene {i}, colorful environment, "
                    "clear subject, gentle cinematic camera movement."
                ),
                "duration_seconds":duration,
                "subtitle_text":f"Scene {i} narration for the story.",
                "camera":"slow_push",
                "motion":"gentle",
                "music_mood":"warm",
            })

        return json.dumps({
            "title":"Mock Story",
            "hook":"A small adventure begins.",
            "language":"English",
            "category":"general",
            "target_duration_seconds":target,
            "scenes":scenes,
        })

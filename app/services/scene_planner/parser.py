from __future__ import annotations

import json
from typing import Any

from app.services.ai.interfaces import GenerationResult
from app.services.scene_planner.models import SceneSpec, StoryPlan


def _payload(data: str | dict[str, Any] | GenerationResult) -> dict[str, Any]:
    if isinstance(data, GenerationResult):
        value = data.output.get("text", data.output)
        if isinstance(value, str):
            return json.loads(value)
        if isinstance(value, dict):
            return value
        raise ValueError("LLM GenerationResult output does not contain JSON text")
    if isinstance(data, str):
        return json.loads(data)
    return data


def parse_story_plan(data: str | dict[str, Any] | GenerationResult) -> StoryPlan:
    payload = _payload(data)
    scenes: list[SceneSpec] = []

    for index, item in enumerate(payload.get("scenes", []), 1):
        sequence = int(item.get("sequence", item.get("number", index)))
        scene_id = str(item.get("scene_id", f"scene-{sequence}"))
        narration = str(item.get("narration", ""))
        scenes.append(
            SceneSpec(
                scene_id=scene_id,
                sequence=sequence,
                narration=narration,
                visual_prompt=str(item.get("visual_prompt", "")),
                duration_seconds=float(item.get("duration_seconds", 8)),
                subtitle_text=str(item.get("subtitle_text", narration)),
                camera=str(item.get("camera", "static")),
                motion=str(item.get("motion", "gentle")),
                music_mood=str(item.get("music_mood", "neutral")),
                metadata=dict(item.get("metadata", {})),
            )
        )

    return StoryPlan(
        title=str(payload.get("title", "Untitled")),
        hook=str(payload.get("hook", "")),
        language=str(payload.get("language", "English")),
        category=str(payload.get("category", "general")),
        target_duration_seconds=float(payload.get("target_duration_seconds", 0)),
        scenes=tuple(sorted(scenes, key=lambda s: s.sequence)),
        metadata=dict(payload.get("metadata", {})),
    )

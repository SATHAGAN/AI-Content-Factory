from __future__ import annotations

import json

from app.services.scene_planner.models import SceneSpec, StoryPlan


def parse_story_plan(data: str | dict) -> StoryPlan:
    payload=json.loads(data) if isinstance(data,str) else data

    scenes=[]
    for item in payload.get("scenes",[]):
        scenes.append(SceneSpec(
            scene_id=str(item["scene_id"]),
            sequence=int(item["sequence"]),
            narration=str(item["narration"]),
            visual_prompt=str(item["visual_prompt"]),
            duration_seconds=float(item["duration_seconds"]),
            subtitle_text=str(item.get("subtitle_text",item["narration"])),
            camera=str(item.get("camera","static")),
            motion=str(item.get("motion","gentle")),
            music_mood=str(item.get("music_mood","neutral")),
            metadata=dict(item.get("metadata",{})),
        ))

    return StoryPlan(
        title=str(payload["title"]),
        hook=str(payload.get("hook","")),
        language=str(payload.get("language","English")),
        category=str(payload.get("category","general")),
        target_duration_seconds=float(payload["target_duration_seconds"]),
        scenes=tuple(sorted(scenes,key=lambda s:s.sequence)),
        metadata=dict(payload.get("metadata",{})),
    )

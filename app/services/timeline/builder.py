from __future__ import annotations

from app.services.timeline.models import SceneClip, Timeline


class TimelineBuilder:
    def build(self, clips: list[SceneClip]) -> Timeline:
        if not clips:
            raise ValueError("At least one scene clip is required")

        ordered=sorted(clips,key=lambda c: c.metadata.get("sequence",0))
        for clip in ordered:
            if clip.duration_seconds <= 0:
                raise ValueError(f"Invalid duration for scene {clip.scene_id}")
            if not clip.video_path:
                raise ValueError(f"Missing video for scene {clip.scene_id}")

        return Timeline(
            clips=tuple(ordered),
            total_duration_seconds=sum(c.duration_seconds for c in ordered),
        )

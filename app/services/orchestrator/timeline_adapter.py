from __future__ import annotations

from app.services.timeline.models import SceneClip


class TimelineAdapter:
    def __init__(self, merge_service):
        self.merge_service=merge_service

    def to_scene_clips(self, generated):
        clips=[]
        for scene,video,audio in generated:
            clips.append(SceneClip(
                scene_id=scene.scene_id,
                video_path=video.video_path,
                duration_seconds=video.duration_seconds,
                audio_path=audio.audio_path,
                subtitle_path=None,
                title=scene.subtitle_text,
                metadata={"sequence":scene.sequence},
            ))
        return clips

    def merge(self, *, clips, manifest_path, output_path):
        plan=self.merge_service.prepare(
            clips,
            manifest_path,
            output_path,
        )
        # Adapter contract can be switched to a real executor later.
        return {
            "output_path":output_path,
            "timeline":plan["timeline"],
            "manifest":plan["manifest"],
            "command":plan["command"],
        }

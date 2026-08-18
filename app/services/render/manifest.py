from __future__ import annotations

from pathlib import Path

from app.services.render.models import RenderConfig, RenderManifest, SceneArtifact


class RenderManifestBuilder:
    def build(
        self,
        scenes: list[SceneArtifact],
        config: RenderConfig,
    ) -> RenderManifest:
        if not scenes:
            raise ValueError("At least one scene is required")

        ordered = sorted(scenes, key=lambda scene: scene.order)
        seen = set()
        for scene in ordered:
            if scene.scene_id in seen:
                raise ValueError(f"Duplicate scene_id: {scene.scene_id}")
            seen.add(scene.scene_id)
            if scene.duration_seconds <= 0:
                raise ValueError(f"Scene {scene.scene_id} has invalid duration")
            if not Path(scene.video_path).is_file():
                raise FileNotFoundError(scene.video_path)
            if scene.audio_path and not Path(scene.audio_path).is_file():
                raise FileNotFoundError(scene.audio_path)

        if config.add_background_music:
            if not config.background_music_path:
                raise ValueError("background_music_path is required")
            if not Path(config.background_music_path).is_file():
                raise FileNotFoundError(config.background_music_path)

        return RenderManifest(
            scenes=tuple(ordered),
            total_duration_seconds=round(
                sum(scene.duration_seconds for scene in ordered), 6
            ),
            output_path=config.output_path,
            metadata={"scene_count": len(ordered)},
        )

from __future__ import annotations

from app.services.media.manifest import RenderManifest


class MediaPipeline:
    """Orchestration contract for future video/audio generation workers."""

    def validate_manifest(self, manifest: RenderManifest) -> RenderManifest:
        scene_numbers = [scene.scene_number for scene in manifest.scenes]
        if scene_numbers != list(range(1, len(scene_numbers) + 1)):
            raise ValueError("Scene numbers must be sequential starting at 1")

        if any(scene.video_uri is None for scene in manifest.scenes):
            raise ValueError("Every scene must have a generated video artifact before render")

        return manifest

    def estimated_duration(self, manifest: RenderManifest) -> float:
        return sum(scene.duration_seconds for scene in manifest.scenes)

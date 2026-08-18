from __future__ import annotations
from app.services.jobs.registry import WorkerRegistry
from app.services.media.pipeline import MediaPipeline
from app.services.workers.generate_scene import generate_scene


def register_default_workers(registry: WorkerRegistry) -> None:
    pipeline = MediaPipeline()

    def validate_render(payload: dict) -> dict:
        from app.services.media.manifest import RenderManifest
        manifest = RenderManifest.model_validate(payload["manifest"])
        pipeline.validate_manifest(manifest)
        return {
            "project_id": manifest.project_id,
            "duration_seconds": pipeline.estimated_duration(manifest),
            "status": "ready_for_render",
        }

    registry.register("validate_render", validate_render)
    registry.register("generate_scene", generate_scene)

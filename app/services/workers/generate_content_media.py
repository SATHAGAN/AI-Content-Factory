from __future__ import annotations

from app.services.media.scene_orchestrator import SceneOrchestrator
from app.services.media.manifest import write_manifest


def generate_content_media(
    plan: dict,
    *,
    manifest_path: str = "./data/manifests/content_media.json",
    **generation_options,
) -> dict:
    result = SceneOrchestrator().generate_plan(plan, **generation_options)
    result["manifest_path"] = write_manifest(result, manifest_path)
    return result

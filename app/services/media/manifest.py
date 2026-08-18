from __future__ import annotations

import json
from pathlib import Path


def write_manifest(manifest: dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


# Backward-compatible render manifest contract used by earlier media workers.
from pydantic import BaseModel


class RenderScene(BaseModel):
    scene_number: int
    duration_seconds: float
    video_uri: str | None = None


class RenderManifest(BaseModel):
    project_id: str | None = None
    scenes: list[RenderScene]

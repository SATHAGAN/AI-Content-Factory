from __future__ import annotations
from pathlib import Path
from app.services.providers.contracts import Scene, VideoArtifact


class MockVideoProvider:
    provider = "mock"

    def __init__(self, model_id: str = "mock-video-v1"):
        self.model_id = model_id

    def generate(self, scene: Scene, output_dir: str) -> VideoArtifact:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        path = Path(output_dir) / f"{scene.scene_id}.mp4"
        # Provider contract only. Real rendering happens in the real adapter.
        path.write_bytes(b"MOCK_VIDEO")
        return VideoArtifact(
            uri=str(path),
            duration_seconds=scene.duration_seconds,
            provider=self.provider,
            model_id=self.model_id,
        )

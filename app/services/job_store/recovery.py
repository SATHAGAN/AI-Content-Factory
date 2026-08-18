from __future__ import annotations

from app.services.job_store.models import SceneStatus


class RecoveryManager:
    """Converts interrupted RUNNING scenes back to retryable FAILED scenes."""

    def __init__(self, store):
        self.store=store

    def recover_interrupted_job(self, job_id: str):
        recovered=[]
        for scene in self.store.list_scenes(job_id):
            if scene.status == SceneStatus.RUNNING:
                self.store.update_scene(
                    job_id,
                    scene.scene_id,
                    status=SceneStatus.FAILED,
                    error="Worker interrupted; scene is retryable",
                )
                recovered.append(scene.scene_id)
        return recovered

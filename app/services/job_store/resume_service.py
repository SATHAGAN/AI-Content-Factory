from __future__ import annotations

from app.services.job_store.models import (
    PersistentJobStatus,
    SceneRecord,
    SceneStatus,
)
from app.services.job_store.sqlite_store import SQLiteJobStore


class ResumeService:
    def __init__(self, store: SQLiteJobStore):
        self.store=store

    def mark_scene_running(self, scene: SceneRecord):
        self.store.update_scene(
            scene.job_id,scene.scene_id,
            status=SceneStatus.RUNNING,
            attempts=scene.attempts+1,
            error=None,
        )

    def mark_scene_completed(
        self,
        scene: SceneRecord,
        *,
        video_path: str,
        audio_path: str,
    ):
        self.store.update_scene(
            scene.job_id,scene.scene_id,
            status=SceneStatus.COMPLETED,
            video_path=video_path,
            audio_path=audio_path,
            error=None,
        )

    def mark_scene_failed(self, scene: SceneRecord, error: str):
        self.store.update_scene(
            scene.job_id,scene.scene_id,
            status=SceneStatus.FAILED,
            error=error,
        )

    def resumable(self, job_id: str):
        return self.store.resumable_scenes(job_id)

    def pause(self, job_id: str):
        self.store.update_job(
            job_id,
            status=PersistentJobStatus.PAUSED,
            current_stage="paused",
        )

    def resume(self, job_id: str):
        self.store.update_job(
            job_id,
            status=PersistentJobStatus.RUNNING,
            current_stage="resuming",
            error=None,
        )
        return self.resumable(job_id)

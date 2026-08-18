from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.services.job_store.models import (
    JobRecord,
    PersistentJobStatus,
    SceneRecord,
    SceneStatus,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteJobStore:
    """Small persistent job store for resumable production jobs."""

    def __init__(self, db_path: str = "artifacts/jobs.sqlite3"):
        self.db_path=Path(db_path)
        self.db_path.parent.mkdir(parents=True,exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_stage TEXT NOT NULL,
                    target_duration REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error TEXT,
                    metadata TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS scenes (
                    job_id TEXT NOT NULL,
                    scene_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    video_path TEXT,
                    audio_path TEXT,
                    error TEXT,
                    metadata TEXT NOT NULL,
                    PRIMARY KEY(job_id,scene_id)
                )
            """)
            db.commit()

    def create_job(
        self,
        *,
        job_id: str,
        channel_id: str,
        target_duration_seconds: float,
        metadata: dict | None = None,
    ):
        now=utc_now()
        with self._connect() as db:
            db.execute(
                """INSERT INTO jobs
                (job_id,channel_id,status,current_stage,target_duration,
                 created_at,updated_at,error,metadata)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    job_id,channel_id,PersistentJobStatus.CREATED.value,
                    "created",target_duration_seconds,now,now,None,
                    json.dumps(metadata or {}),
                ),
            )
            db.commit()

    def get_job(self, job_id: str) -> JobRecord:
        with self._connect() as db:
            row=db.execute(
                "SELECT job_id,channel_id,status,current_stage,target_duration,"
                "created_at,updated_at,error,metadata FROM jobs WHERE job_id=?",
                (job_id,),
            ).fetchone()
        if row is None:
            raise KeyError(job_id)
        return JobRecord(
            job_id=row[0],channel_id=row[1],
            status=PersistentJobStatus(row[2]),
            current_stage=row[3],target_duration_seconds=row[4],
            created_at=row[5],updated_at=row[6],error=row[7],
            metadata=json.loads(row[8]),
        )

    def update_job(
        self,
        job_id: str,
        *,
        status: PersistentJobStatus | None = None,
        current_stage: str | None = None,
        error: str | None = None,
    ):
        current=self.get_job(job_id)
        with self._connect() as db:
            db.execute(
                """UPDATE jobs SET status=?,current_stage=?,updated_at=?,error=?
                   WHERE job_id=?""",
                (
                    (status or current.status).value,
                    current_stage or current.current_stage,
                    utc_now(),
                    error,
                    job_id,
                ),
            )
            db.commit()

    def add_scenes(self, scenes):
        with self._connect() as db:
            for scene in scenes:
                db.execute(
                    """INSERT OR IGNORE INTO scenes
                    (job_id,scene_id,sequence,status,attempts,video_path,
                     audio_path,error,metadata)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                    (
                        scene.job_id,scene.scene_id,scene.sequence,
                        scene.status.value,scene.attempts,scene.video_path,
                        scene.audio_path,scene.error,
                        json.dumps(scene.metadata),
                    ),
                )
            db.commit()

    def update_scene(
        self,
        job_id: str,
        scene_id: str,
        *,
        status: SceneStatus,
        attempts: int | None = None,
        video_path: str | None = None,
        audio_path: str | None = None,
        error: str | None = None,
    ):
        with self._connect() as db:
            row=db.execute(
                "SELECT attempts,video_path,audio_path FROM scenes "
                "WHERE job_id=? AND scene_id=?",
                (job_id,scene_id),
            ).fetchone()
            if row is None:
                raise KeyError(f"{job_id}/{scene_id}")

            db.execute(
                """UPDATE scenes SET status=?,attempts=?,video_path=?,
                   audio_path=?,error=? WHERE job_id=? AND scene_id=?""",
                (
                    status.value,
                    row[0] if attempts is None else attempts,
                    row[1] if video_path is None else video_path,
                    row[2] if audio_path is None else audio_path,
                    error,
                    job_id,scene_id,
                ),
            )
            db.commit()

    def list_scenes(self, job_id: str) -> list[SceneRecord]:
        with self._connect() as db:
            rows=db.execute(
                """SELECT job_id,scene_id,sequence,status,attempts,
                   video_path,audio_path,error,metadata
                   FROM scenes WHERE job_id=? ORDER BY sequence""",
                (job_id,),
            ).fetchall()

        return [
            SceneRecord(
                job_id=r[0],scene_id=r[1],sequence=r[2],
                status=SceneStatus(r[3]),attempts=r[4],
                video_path=r[5],audio_path=r[6],error=r[7],
                metadata=json.loads(r[8]),
            )
            for r in rows
        ]

    def resumable_scenes(self, job_id: str) -> list[SceneRecord]:
        return [
            s for s in self.list_scenes(job_id)
            if s.status != SceneStatus.COMPLETED
        ]

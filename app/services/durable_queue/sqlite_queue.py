from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.services.durable_queue.models import QueueTask, TaskState, LeasedTask


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat()


class SQLiteTaskQueue:
    """Durable task queue with worker leases.

    This V1 implementation uses SQLite so it works locally and remains
    replaceable by Redis/SQS/RabbitMQ later.
    """

    def __init__(self, db_path: str = "artifacts/queue.sqlite3"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS queue_tasks (
                    task_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    max_attempts INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    worker_id TEXT,
                    lease_until TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_queue_ready
                ON queue_tasks(state, priority DESC, created_at ASC)
            """)
            db.commit()

    def enqueue(self, task: QueueTask) -> None:
        now = iso(utc_now())
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO queue_tasks
                (task_id,job_id,task_type,payload,priority,max_attempts,state,
                 attempts,worker_id,lease_until,error,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    task.task_id,
                    task.job_id,
                    task.task_type,
                    json.dumps(task.payload),
                    task.priority,
                    task.max_attempts,
                    TaskState.QUEUED.value,
                    0,
                    None,
                    None,
                    None,
                    now,
                    now,
                ),
            )
            db.commit()

    def _recover_expired_leases(self, db) -> None:
        now = iso(utc_now())
        db.execute(
            """
            UPDATE queue_tasks
            SET state=?, worker_id=NULL, lease_until=NULL,
                updated_at=?, error=?
            WHERE state=? AND lease_until IS NOT NULL AND lease_until < ?
            """,
            (
                TaskState.QUEUED.value,
                now,
                "Worker lease expired; task returned to queue",
                TaskState.LEASED.value,
                now,
            ),
        )

    def claim(
        self,
        worker_id: str,
        *,
        lease_seconds: int = 300,
    ) -> LeasedTask | None:
        with self._connect() as db:
            self._recover_expired_leases(db)

            row = db.execute(
                """
                SELECT task_id,job_id,task_type,payload,priority,max_attempts,
                       attempts
                FROM queue_tasks
                WHERE state=?
                  AND attempts < max_attempts
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                """,
                (TaskState.QUEUED.value,),
            ).fetchone()

            if row is None:
                db.commit()
                return None

            task_id, job_id, task_type, payload, priority, max_attempts, attempts = row
            next_attempt = attempts + 1
            lease_until = utc_now() + timedelta(seconds=lease_seconds)
            now = iso(utc_now())

            updated = db.execute(
                """
                UPDATE queue_tasks
                SET state=?, attempts=?, worker_id=?, lease_until=?,
                    updated_at=?, error=NULL
                WHERE task_id=? AND state=?
                """,
                (
                    TaskState.LEASED.value,
                    next_attempt,
                    worker_id,
                    iso(lease_until),
                    now,
                    task_id,
                    TaskState.QUEUED.value,
                ),
            ).rowcount

            db.commit()

        if updated != 1:
            return None

        task = QueueTask(
            task_id=task_id,
            job_id=job_id,
            task_type=task_type,
            payload=json.loads(payload),
            priority=priority,
            max_attempts=max_attempts,
        )
        return LeasedTask(
            task=task,
            worker_id=worker_id,
            attempt=next_attempt,
            lease_until=iso(lease_until),
        )

    def heartbeat(self, task_id: str, worker_id: str, *, lease_seconds: int = 300) -> bool:
        lease_until = utc_now() + timedelta(seconds=lease_seconds)
        with self._connect() as db:
            changed = db.execute(
                """
                UPDATE queue_tasks
                SET lease_until=?, updated_at=?
                WHERE task_id=? AND worker_id=? AND state=?
                """,
                (
                    iso(lease_until),
                    iso(utc_now()),
                    task_id,
                    worker_id,
                    TaskState.LEASED.value,
                ),
            ).rowcount
            db.commit()
        return changed == 1

    def complete(self, task_id: str, worker_id: str) -> bool:
        with self._connect() as db:
            changed = db.execute(
                """
                UPDATE queue_tasks
                SET state=?, worker_id=NULL, lease_until=NULL,
                    updated_at=?, error=NULL
                WHERE task_id=? AND worker_id=? AND state=?
                """,
                (
                    TaskState.COMPLETED.value,
                    iso(utc_now()),
                    task_id,
                    worker_id,
                    TaskState.LEASED.value,
                ),
            ).rowcount
            db.commit()
        return changed == 1

    def fail(self, task_id: str, worker_id: str, error: str) -> TaskState:
        with self._connect() as db:
            row = db.execute(
                """
                SELECT attempts,max_attempts
                FROM queue_tasks
                WHERE task_id=? AND worker_id=? AND state=?
                """,
                (task_id, worker_id, TaskState.LEASED.value),
            ).fetchone()

            if row is None:
                raise KeyError(f"Leased task not found: {task_id}")

            attempts, max_attempts = row
            final_state = (
                TaskState.FAILED
                if attempts >= max_attempts
                else TaskState.QUEUED
            )

            db.execute(
                """
                UPDATE queue_tasks
                SET state=?, worker_id=NULL, lease_until=NULL,
                    updated_at=?, error=?
                WHERE task_id=?
                """,
                (
                    final_state.value,
                    iso(utc_now()),
                    error,
                    task_id,
                ),
            )
            db.commit()

        return final_state

    def get_state(self, task_id: str) -> TaskState:
        with self._connect() as db:
            row = db.execute(
                "SELECT state FROM queue_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
        if row is None:
            raise KeyError(task_id)
        return TaskState(row[0])

    def pending_count(self) -> int:
        with self._connect() as db:
            row = db.execute(
                "SELECT COUNT(*) FROM queue_tasks WHERE state=?",
                (TaskState.QUEUED.value,),
            ).fetchone()
        return int(row[0])

    def get_attempts(self, task_id: str) -> int:
        with self._connect() as db:
            row = db.execute(
                "SELECT attempts FROM queue_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
        if row is None:
            raise KeyError(task_id)
        return int(row[0])

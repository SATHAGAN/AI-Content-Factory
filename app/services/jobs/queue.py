from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from app.models.enums import JobStatus


@dataclass
class QueuedJob:
    id: str
    job_type: str
    payload: dict
    priority: int = 100
    status: JobStatus = JobStatus.QUEUED
    attempts: int = 0
    max_attempts: int = 3
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class InMemoryJobQueue:
    """Development queue contract.

    Production will use Redis/Celery or a managed equivalent. Keeping the
    queue behind this interface prevents the API from being coupled to a
    particular queue technology.
    """

    def __init__(self):
        self._jobs: dict[str, QueuedJob] = {}
        self._lock = Lock()

    def enqueue(self, job_type: str, payload: dict, priority: int = 100, max_attempts: int = 3) -> QueuedJob:
        job = QueuedJob(
            id=str(uuid4()),
            job_type=job_type,
            payload=payload,
            priority=priority,
            max_attempts=max_attempts,
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> QueuedJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list(self) -> list[QueuedJob]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda item: (item.priority, item.created_at or datetime.min))

    def mark_running(self, job_id: str) -> QueuedJob:
        with self._lock:
            job = self._jobs[job_id]
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            job.attempts += 1
            return job

    def mark_succeeded(self, job_id: str) -> QueuedJob:
        with self._lock:
            job = self._jobs[job_id]
            job.status = JobStatus.SUCCEEDED
            job.finished_at = datetime.now(timezone.utc)
            job.error = None
            return job

    def mark_failed(self, job_id: str, error: str) -> QueuedJob:
        with self._lock:
            job = self._jobs[job_id]
            job.error = error
            if job.attempts < job.max_attempts:
                job.status = JobStatus.RETRYING
            else:
                job.status = JobStatus.FAILED
                job.finished_at = datetime.now(timezone.utc)
            return job

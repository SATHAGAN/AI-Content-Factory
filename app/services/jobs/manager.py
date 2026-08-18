from __future__ import annotations

from app.services.jobs.queue import InMemoryJobQueue, QueuedJob


class JobManager:
    def __init__(self, queue: InMemoryJobQueue):
        self.queue = queue

    def submit(self, job_type: str, payload: dict, priority: int = 100) -> QueuedJob:
        return self.queue.enqueue(job_type, payload, priority=priority)

    def retry(self, job_id: str) -> QueuedJob:
        job = self.queue.get(job_id)
        if not job:
            raise KeyError(job_id)
        if job.status.value not in {"retrying", "failed"}:
            raise ValueError("Only failed or retrying jobs can be retried")
        if job.attempts >= job.max_attempts:
            raise ValueError("Maximum attempts reached")
        job.status = type(job.status).QUEUED
        job.error = None
        return job

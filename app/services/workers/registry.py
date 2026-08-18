from __future__ import annotations

from threading import Lock
from typing import Callable


class JobRegistry:
    """Thread-safe in-process job state store for the local V1 worker.

    The interface is deliberately small so it can later be backed by Redis
    or PostgreSQL without changing the pipeline contract.
    """

    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._lock = Lock()

    def put(self, job_id: str, value: dict) -> None:
        with self._lock:
            self._jobs[job_id] = dict(value)

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            value = self._jobs.get(job_id)
            return None if value is None else dict(value)

    def update(self, job_id: str, **changes) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(job_id)
            self._jobs[job_id].update(changes)
            return dict(self._jobs[job_id])

    def all(self, organization_id: str | None = None) -> list[dict]:
        with self._lock:
            values = list(self._jobs.values())
        if organization_id is not None:
            values = [x for x in values if x.get("organization_id") == organization_id]
        return [dict(x) for x in values]


job_registry = JobRegistry()

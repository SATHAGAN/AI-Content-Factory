from __future__ import annotations

from datetime import datetime,timezone


class WorkerHeartbeat:
    def __init__(self):
        self._last_seen={}

    def beat(self, worker_id: str):
        self._last_seen[worker_id]=datetime.now(timezone.utc).isoformat()

    def last_seen(self, worker_id: str):
        return self._last_seen.get(worker_id)

    def stale(self, worker_id: str, *, max_age_seconds: float, now=None):
        if worker_id not in self._last_seen:
            return True
        current=now or datetime.now(timezone.utc)
        then=datetime.fromisoformat(self._last_seen[worker_id])
        return (current-then).total_seconds() > max_age_seconds

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JobState:
    status: str = "queued"
    stage: str = "queued"
    attempts: int = 0
    error: str | None = None


class ProductionStateStore:
    def __init__(self):
        self._states: dict[str, JobState] = {}

    def get(self, job_id: str) -> JobState:
        return self._states.setdefault(job_id, JobState())

    def transition(self, job_id: str, *, status: str, stage: str, error: str | None = None):
        state=self.get(job_id)
        state.status=status
        state.stage=stage
        state.error=error
        return state

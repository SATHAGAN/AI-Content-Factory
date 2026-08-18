from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TaskState(str, Enum):
    QUEUED = "queued"
    LEASED = "leased"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class QueueTask:
    task_id: str
    job_id: str
    task_type: str
    payload: dict = field(default_factory=dict)
    priority: int = 0
    max_attempts: int = 3


@dataclass(frozen=True)
class LeasedTask:
    task: QueueTask
    worker_id: str
    attempt: int
    lease_until: str

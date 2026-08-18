from __future__ import annotations

from collections.abc import Callable
from typing import Any


Handler = Callable[[dict[str, Any]], dict[str, Any]]


class WorkerRegistry:
    def __init__(self):
        self._handlers: dict[str, Handler] = {}

    def register(self, job_type: str, handler: Handler) -> None:
        if job_type in self._handlers:
            raise ValueError(f"Handler already registered for {job_type}")
        self._handlers[job_type] = handler

    def get(self, job_type: str) -> Handler:
        try:
            return self._handlers[job_type]
        except KeyError as exc:
            raise KeyError(f"No worker registered for job type: {job_type}") from exc

    def types(self) -> list[str]:
        return sorted(self._handlers)

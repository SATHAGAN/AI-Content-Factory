from __future__ import annotations


class DurableDispatcher:
    """Connects the existing worker registry with the durable queue."""

    def __init__(self, registry, queue):
        self.registry = registry
        self.queue = queue

    def dispatch(self, worker_id: str, *, lease_seconds: int = 300):
        worker = self.registry.get(worker_id)

        if worker.status.value != "idle":
            raise RuntimeError(f"Worker {worker_id} is not idle")

        leased = self.queue.claim(
            worker_id,
            lease_seconds=lease_seconds,
        )

        if leased is None:
            return None

        self.registry.claim(worker_id, leased.task.job_id)
        return leased

    def complete(self, worker_id: str, task_id: str) -> bool:
        completed = self.queue.complete(task_id, worker_id)
        if completed:
            self.registry.release(worker_id)
        return completed

    def fail(self, worker_id: str, task_id: str, error: str):
        state = self.queue.fail(task_id, worker_id, error)
        self.registry.release(worker_id)
        return state

from __future__ import annotations


class WorkerQueueClient:
    """Thin worker-side communication boundary."""

    def __init__(self, queue, worker_id: str):
        self.queue = queue
        self.worker_id = worker_id

    def poll(self, *, lease_seconds: int = 300):
        return self.queue.claim(
            self.worker_id,
            lease_seconds=lease_seconds,
        )

    def heartbeat(self, task_id: str, *, lease_seconds: int = 300):
        return self.queue.heartbeat(
            task_id,
            self.worker_id,
            lease_seconds=lease_seconds,
        )

    def ack(self, task_id: str):
        return self.queue.complete(task_id, self.worker_id)

    def reject(self, task_id: str, error: str):
        return self.queue.fail(task_id, self.worker_id, error)

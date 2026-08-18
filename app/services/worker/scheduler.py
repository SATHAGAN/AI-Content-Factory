from __future__ import annotations

from app.services.worker.models import WorkerTask


class WorkerScheduler:
    def __init__(self, registry):
        self.registry=registry

    def choose(self, task: WorkerTask):
        candidates=self.registry.available(task)
        if not candidates:
            raise RuntimeError(
                f"No available worker for task {task.task_id}"
            )
        # Prefer the worker with the highest advertised VRAM.
        return max(
            candidates,
            key=lambda worker: worker.capabilities.vram_gb,
        )

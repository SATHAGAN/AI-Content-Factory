from __future__ import annotations

from app.services.worker.models import Worker,WorkerStatus,WorkerTask


class WorkerRegistry:
    def __init__(self):
        self._workers={}

    def register(self, worker: Worker):
        if worker.capabilities.worker_id in self._workers:
            raise ValueError("Worker already registered")
        worker.status=WorkerStatus.IDLE
        self._workers[worker.capabilities.worker_id]=worker

    def get(self, worker_id: str) -> Worker:
        return self._workers[worker_id]

    def all(self):
        return list(self._workers.values())

    def available(self, task: WorkerTask):
        result=[]
        for worker in self._workers.values():
            if worker.status != WorkerStatus.IDLE:
                continue
            caps=worker.capabilities
            if not all(getattr(caps, name, False) for name in task.required_capabilities):
                continue
            if task.preferred_models:
                if not set(task.preferred_models).intersection(caps.models):
                    continue
            result.append(worker)
        return result

    def claim(self, worker_id: str, job_id: str):
        worker=self.get(worker_id)
        if worker.status != WorkerStatus.IDLE:
            raise RuntimeError("Worker is not idle")
        worker.status=WorkerStatus.BUSY
        worker.current_job_id=job_id

    def release(self, worker_id: str):
        worker=self.get(worker_id)
        worker.status=WorkerStatus.IDLE
        worker.current_job_id=None

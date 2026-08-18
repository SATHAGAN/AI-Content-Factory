from __future__ import annotations


class WorkerDispatcher:
    def __init__(self, registry, scheduler, queue):
        self.registry=registry
        self.scheduler=scheduler
        self.queue=queue

    def dispatch_one(self):
        task=self.queue.dequeue()
        if task is None:
            return None

        worker=self.scheduler.choose(task)
        self.registry.claim(
            worker.capabilities.worker_id,
            task.job_id,
        )
        return worker,task

    def complete(self, worker_id: str):
        self.registry.release(worker_id)

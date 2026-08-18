from __future__ import annotations

from app.services.inference.worker_profile import GPUWorkerProfile,supports


class GPUWorkerRouter:
    def __init__(self, workers: list[GPUWorkerProfile]):
        self.workers=workers

    def select(self, *, task: str, required_vram_gb: float | None = None):
        compatible=[
            worker for worker in self.workers
            if supports(
                worker,
                task=task,
                required_vram_gb=required_vram_gb,
            )
        ]
        if not compatible:
            raise RuntimeError(
                f"No GPU worker supports task={task} "
                f"required_vram_gb={required_vram_gb}"
            )
        return sorted(compatible,key=lambda w:w.vram_gb)[0]

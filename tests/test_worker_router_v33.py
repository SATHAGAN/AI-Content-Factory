import pytest

from app.services.inference.worker_profile import GPUWorkerProfile
from app.services.inference.worker_router import GPUWorkerRouter


def test_router_selects_smallest_compatible_worker():
    router=GPUWorkerRouter([
        GPUWorkerProfile("large","A",48),
        GPUWorkerProfile("small","B",24),
    ])
    worker=router.select(task="video",required_vram_gb=20)
    assert worker.worker_id=="small"


def test_router_rejects_insufficient_vram():
    router=GPUWorkerRouter([
        GPUWorkerProfile("small","B",12),
    ])
    with pytest.raises(RuntimeError):
        router.select(task="video",required_vram_gb=24)


def test_router_checks_task_support():
    router=GPUWorkerRouter([
        GPUWorkerProfile("tts-only","B",24,enabled_tasks=("tts",)),
    ])
    with pytest.raises(RuntimeError):
        router.select(task="video",required_vram_gb=8)

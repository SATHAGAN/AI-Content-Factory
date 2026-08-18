import pytest

from app.services.worker.models import (
    Worker,WorkerCapabilities,WorkerKind,WorkerTask,WorkerStatus
)
from app.services.worker.registry import WorkerRegistry
from app.services.worker.scheduler import WorkerScheduler
from app.services.worker.queue import InMemoryTaskQueue
from app.services.worker.dispatcher import WorkerDispatcher


def gpu(worker_id="gpu-1",vram=12):
    return Worker(WorkerCapabilities(
        worker_id=worker_id,
        kind=WorkerKind.GPU,
        video=True,tts=True,qa=True,ffmpeg=True,
        vram_gb=vram,
        models=("video-a","tts-a"),
    ))


def cpu(worker_id="cpu-1"):
    return Worker(WorkerCapabilities(
        worker_id=worker_id,
        kind=WorkerKind.CPU,
        video=False,tts=False,qa=True,ffmpeg=True,
        vram_gb=0,
        models=(),
    ))


def test_registry_and_capability_matching():
    registry=WorkerRegistry()
    registry.register(gpu())
    registry.register(cpu())

    task=WorkerTask(
        task_id="t1",
        job_id="j1",
        task_type="video",
        required_capabilities=("video",),
        preferred_models=("video-a",),
    )
    assert [w.capabilities.worker_id for w in registry.available(task)]==["gpu-1"]


def test_scheduler_prefers_highest_vram():
    registry=WorkerRegistry()
    registry.register(gpu("gpu-small",8))
    registry.register(gpu("gpu-large",24))
    scheduler=WorkerScheduler(registry)
    task=WorkerTask(
        task_id="t2",
        job_id="j2",
        task_type="video",
        required_capabilities=("video",),
    )
    assert scheduler.choose(task).capabilities.worker_id=="gpu-large"


def test_queue_priority_and_fifo():
    queue=InMemoryTaskQueue()
    low=WorkerTask("low","j1","video",priority=1)
    high=WorkerTask("high","j2","video",priority=10)
    high2=WorkerTask("high2","j3","video",priority=10)
    queue.enqueue(low); queue.enqueue(high); queue.enqueue(high2)
    assert queue.dequeue().task_id=="high"
    assert queue.dequeue().task_id=="high2"
    assert queue.dequeue().task_id=="low"


def test_dispatch_claim_and_release():
    registry=WorkerRegistry()
    registry.register(gpu())
    scheduler=WorkerScheduler(registry)
    queue=InMemoryTaskQueue()
    queue.enqueue(WorkerTask(
        "t3","j3","video",
        required_capabilities=("video",),
    ))
    dispatcher=WorkerDispatcher(registry,scheduler,queue)
    worker,task=dispatcher.dispatch_one()
    assert worker.status==WorkerStatus.BUSY
    assert worker.current_job_id=="j3"
    dispatcher.complete(worker.capabilities.worker_id)
    assert worker.status==WorkerStatus.IDLE
    assert worker.current_job_id is None


def test_no_worker_fails_fast():
    registry=WorkerRegistry()
    scheduler=WorkerScheduler(registry)
    queue=InMemoryTaskQueue()
    queue.enqueue(WorkerTask(
        "t4","j4","video",
        required_capabilities=("video",),
    ))
    dispatcher=WorkerDispatcher(registry,scheduler,queue)
    with pytest.raises(RuntimeError):
        dispatcher.dispatch_one()

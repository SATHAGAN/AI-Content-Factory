from app.services.durable_queue.models import QueueTask
from app.services.durable_queue.sqlite_queue import SQLiteTaskQueue
from app.services.durable_queue.dispatcher import DurableDispatcher
from app.services.worker.models import Worker, WorkerCapabilities, WorkerKind
from app.services.worker.registry import WorkerRegistry


def test_dispatcher_integrates_worker_registry(tmp_path):
    queue = SQLiteTaskQueue(str(tmp_path / "queue.sqlite3"))
    queue.enqueue(QueueTask(
        task_id="t1",
        job_id="job-1",
        task_type="video",
    ))

    registry = WorkerRegistry()
    registry.register(Worker(WorkerCapabilities(
        worker_id="gpu-1",
        kind=WorkerKind.GPU,
        video=True,
        tts=True,
        qa=True,
        ffmpeg=True,
        vram_gb=16,
        models=("video-a",),
    )))

    dispatcher = DurableDispatcher(registry, queue)
    leased = dispatcher.dispatch("gpu-1")

    assert leased is not None
    assert registry.get("gpu-1").current_job_id == "job-1"

    assert dispatcher.complete("gpu-1", "t1")
    assert registry.get("gpu-1").current_job_id is None

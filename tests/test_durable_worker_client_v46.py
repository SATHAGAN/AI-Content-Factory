from app.services.durable_queue.models import QueueTask, TaskState
from app.services.durable_queue.sqlite_queue import SQLiteTaskQueue
from app.services.durable_queue.worker_client import WorkerQueueClient


def test_worker_client_lifecycle(tmp_path):
    queue = SQLiteTaskQueue(str(tmp_path / "queue.sqlite3"))
    queue.enqueue(QueueTask(
        task_id="t1",
        job_id="j1",
        task_type="tts",
    ))

    client = WorkerQueueClient(queue, "worker-1")
    leased = client.poll()
    assert leased is not None

    assert client.heartbeat("t1")
    assert client.ack("t1")
    assert queue.get_state("t1") == TaskState.COMPLETED

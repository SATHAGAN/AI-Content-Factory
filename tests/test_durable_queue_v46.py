from app.services.durable_queue.models import QueueTask, TaskState
from app.services.durable_queue.sqlite_queue import SQLiteTaskQueue


def make_queue(tmp_path):
    return SQLiteTaskQueue(str(tmp_path / "queue.sqlite3"))


def task(task_id, priority=0, max_attempts=3):
    return QueueTask(
        task_id=task_id,
        job_id=f"job-{task_id}",
        task_type="video",
        payload={"scene": task_id},
        priority=priority,
        max_attempts=max_attempts,
    )


def test_enqueue_claim_and_complete(tmp_path):
    queue = make_queue(tmp_path)
    queue.enqueue(task("a"))

    leased = queue.claim("worker-1")
    assert leased is not None
    assert leased.worker_id == "worker-1"
    assert leased.attempt == 1
    assert queue.get_state("a") == TaskState.LEASED

    assert queue.complete("a", "worker-1")
    assert queue.get_state("a") == TaskState.COMPLETED
    assert queue.pending_count() == 0


def test_priority_order(tmp_path):
    queue = make_queue(tmp_path)
    queue.enqueue(task("low", priority=1))
    queue.enqueue(task("high", priority=10))

    leased = queue.claim("worker-1")
    assert leased.task.task_id == "high"


def test_heartbeat_requires_owner(tmp_path):
    queue = make_queue(tmp_path)
    queue.enqueue(task("a"))

    leased = queue.claim("worker-1")
    assert leased is not None

    assert not queue.heartbeat("a", "worker-2")
    assert queue.heartbeat("a", "worker-1")


def test_failed_task_is_requeued_until_attempt_limit(tmp_path):
    queue = make_queue(tmp_path)
    queue.enqueue(task("a", max_attempts=2))

    first = queue.claim("worker-1")
    assert first.attempt == 1
    assert queue.fail("a", "worker-1", "temporary") == TaskState.QUEUED

    second = queue.claim("worker-2")
    assert second.attempt == 2
    assert queue.fail("a", "worker-2", "permanent") == TaskState.FAILED
    assert queue.get_state("a") == TaskState.FAILED


def test_claim_does_not_exceed_max_attempts(tmp_path):
    queue = make_queue(tmp_path)
    queue.enqueue(task("a", max_attempts=1))

    leased = queue.claim("worker-1")
    assert leased.attempt == 1
    queue.fail("a", "worker-1", "failed")

    assert queue.claim("worker-2") is None

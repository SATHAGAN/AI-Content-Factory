from app.models.enums import JobStatus
from app.services.jobs.queue import InMemoryJobQueue


def test_job_queue_lifecycle_and_retry():
    queue = InMemoryJobQueue()
    job = queue.enqueue("video_scene", {"scene": 1}, max_attempts=2)

    assert job.status == JobStatus.QUEUED
    running = queue.mark_running(job.id)
    assert running.status == JobStatus.RUNNING
    assert running.attempts == 1

    retrying = queue.mark_failed(job.id, "temporary GPU failure")
    assert retrying.status == JobStatus.RETRYING

    queue.mark_running(job.id)
    failed = queue.mark_failed(job.id, "second failure")
    assert failed.status == JobStatus.FAILED


def test_priority_order():
    queue = InMemoryJobQueue()
    low = queue.enqueue("bulk", {}, priority=200)
    high = queue.enqueue("preview", {}, priority=10)

    assert [j.id for j in queue.list()] == [high.id, low.id]

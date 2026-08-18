
from app.services.pipeline.worker import generation_worker
from app.services.workers.registry import job_registry


def test_worker_reaches_approval():
    job_id = "worker-test"
    job_registry.put(job_id, {
        "id": job_id,
        "organization_id": "org",
        "status": "queued",
        "stage": "queued",
        "progress": 0,
    })
    result = generation_worker.run(job_id)
    assert result["status"] == "awaiting_approval"
    assert result["stage"] == "approval"
    assert result["progress"] == 100


def test_worker_preserves_job_id():
    job_id = "worker-test-2"
    job_registry.put(job_id, {"id": job_id, "organization_id": "org", "status": "queued"})
    result = generation_worker.run(job_id)
    assert result["id"] == job_id

import pytest

from app.services.jobs.registry import WorkerRegistry
from app.services.jobs.workers import register_default_workers


def test_worker_registry():
    registry = WorkerRegistry()
    register_default_workers(registry)
    assert "validate_render" in registry.types()

    result = registry.get("validate_render")({
        "manifest": {
            "project_id": "p1",
            "scenes": [
                {"scene_number": 1, "duration_seconds": 5, "video_uri": "gs://b/1.mp4"}
            ],
        }
    })
    assert result["status"] == "ready_for_render"
    assert result["duration_seconds"] == 5


def test_unknown_worker():
    registry = WorkerRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")

from pathlib import Path

from app.services.video.mock import MockVideoProvider
from app.services.video.models import VideoGenerationRequest
from app.services.video.selector import VideoModelSelector, WorkerVideoProfile
from app.services.video.service import VideoGenerationService


def test_model_is_discovered(tmp_path):
    provider = MockVideoProvider(str(tmp_path))
    models = provider.list_models()
    assert models[0].model_id == "mock-video-v1"


def test_selector_respects_duration(tmp_path):
    provider = MockVideoProvider(str(tmp_path))
    selector = VideoModelSelector([provider])

    selected = selector.select(VideoGenerationRequest(
        job_id="job-1",
        prompt="a story",
        duration_seconds=10,
    ))
    assert selected.model_id == "mock-video-v1"


def test_selector_rejects_too_long_video(tmp_path):
    provider = MockVideoProvider(str(tmp_path))
    selector = VideoModelSelector([provider])

    try:
        selector.select(VideoGenerationRequest(
            job_id="job-1",
            prompt="a story",
            duration_seconds=61,
        ))
    except ValueError as exc:
        assert "No compatible" in str(exc)
    else:
        raise AssertionError("Expected no compatible model")


def test_selector_respects_vram_profile(tmp_path):
    provider = MockVideoProvider(str(tmp_path))
    selector = VideoModelSelector(
        [provider],
        WorkerVideoProfile(
            worker_id="cpu-worker",
            vram_gb=0,
            providers=("mock",),
        ),
    )
    assert selector.select(VideoGenerationRequest(
        job_id="job-1",
        prompt="story",
        duration_seconds=5,
    )).model_id == "mock-video-v1"


def test_service_generates_artifact(tmp_path):
    provider = MockVideoProvider(str(tmp_path))
    service = VideoGenerationService([provider])

    result = service.generate(VideoGenerationRequest(
        job_id="job-1",
        prompt="A child-friendly animated story",
        duration_seconds=8,
    ))

    assert Path(result.output_path).is_file()
    assert result.provider == "mock"
    assert result.model == "mock-video-v1"
    assert result.metadata["mock"] is True


def test_explicit_unknown_model_fails(tmp_path):
    provider = MockVideoProvider(str(tmp_path))
    service = VideoGenerationService([provider])

    try:
        service.generate(VideoGenerationRequest(
            job_id="job-1",
            prompt="story",
            duration_seconds=5,
            model="does-not-exist",
        ))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected model selection failure")

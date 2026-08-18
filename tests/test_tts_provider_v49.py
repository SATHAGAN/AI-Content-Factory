from pathlib import Path

from app.services.tts.factory import create_tts_provider, get_tts_provider
from app.services.tts.models import TTSRequest
from app.services.tts.mock import MockTTSGenerator
from app.services.tts.selector import TTSModelSelector, TTSWorkerProfile
from app.services.tts.service import TTSGenerationService


def test_factory_returns_legacy_generator_name():
    provider = create_tts_provider("mock")
    assert provider.__class__.__name__ == "MockTTSGenerator"


def test_model_discovery_and_language_voice_selection(tmp_path):
    provider = MockTTSGenerator(str(tmp_path))
    selector = TTSModelSelector([provider])
    model = selector.select(TTSRequest(text="hello", language="ta", voice="child"))
    assert model.model_id == "mock-tts-v1"


def test_vram_filtering(tmp_path):
    provider = MockTTSGenerator(str(tmp_path))
    selector = TTSModelSelector(
        [provider],
        TTSWorkerProfile(worker_id="cpu", vram_gb=0, providers=("mock",)),
    )
    assert selector.select(TTSRequest(text="hello")).model_id == "mock-tts-v1"


def test_generation_returns_duration_and_artifact(tmp_path):
    provider = MockTTSGenerator(str(tmp_path))
    service = TTSGenerationService([provider])
    result = service.synthesize(
        TTSRequest(
            text="This is a small narration for a test.",
            language="en",
            voice="narrator",
            job_id="job-1",
        )
    )
    assert Path(result.audio_path).is_file()
    assert result.duration_seconds > 0
    assert result.sample_rate == 24000


def test_unknown_voice_fails(tmp_path):
    provider = MockTTSGenerator(str(tmp_path))
    service = TTSGenerationService([provider])
    try:
        service.synthesize(TTSRequest(text="hello", voice="unknown"))
    except ValueError as exc:
        assert "No compatible TTS model" in str(exc)
    else:
        raise AssertionError("Expected model selection failure")


def test_environment_factory(monkeypatch):
    monkeypatch.setenv("TTS_PROVIDER", "mock")
    assert isinstance(get_tts_provider(), MockTTSGenerator)

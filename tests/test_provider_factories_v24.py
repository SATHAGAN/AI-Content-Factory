import pytest


def test_mock_video_factory(monkeypatch):
    monkeypatch.setenv("VIDEO_PROVIDER","mock")
    from app.services.media.factory import get_video_provider
    assert get_video_provider().__class__.__name__=="MockVideoGenerator"


def test_diffusers_factory(monkeypatch):
    monkeypatch.setenv("VIDEO_PROVIDER","huggingface-diffusers")
    monkeypatch.setenv("VIDEO_MODEL_ID","test-video-model")
    from app.services.media.factory import get_video_provider
    assert get_video_provider().model_id=="test-video-model"


def test_local_tts_factory(monkeypatch):
    monkeypatch.setenv("TTS_PROVIDER","local-command")
    monkeypatch.setenv("TTS_COMMAND","echo")
    from app.services.tts.factory import get_tts_provider
    assert get_tts_provider().model_id=="local-tts"


def test_unknown_video_provider_rejected(monkeypatch):
    monkeypatch.setenv("VIDEO_PROVIDER","unknown")
    from app.services.media.factory import get_video_provider
    with pytest.raises(ValueError):
        get_video_provider()

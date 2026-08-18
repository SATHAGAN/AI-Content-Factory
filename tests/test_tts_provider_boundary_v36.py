import pytest

from app.services.tts.provider import Qwen3TTSProvider


def test_real_provider_requires_runtime_or_gpu():
    provider=Qwen3TTSProvider("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")
    # Do not download weights during unit tests.
    assert provider.model is None
    assert provider.model_id.endswith("CustomVoice")

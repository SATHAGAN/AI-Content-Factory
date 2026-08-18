from __future__ import annotations

import os

from app.services.tts.models import TTSProvider
from app.services.tts.mock import MockTTSGenerator
from app.services.tts.providers.local_speech import LocalTTSProvider


def create_tts_provider(provider: TTSProvider | str = TTSProvider.MOCK, **kwargs):
    value = str(provider)

    if value == "local-command":
        return LocalTTSProvider(
            command=kwargs.get("command") or os.getenv("TTS_COMMAND"),
            model_id=kwargs.get("model_id") or os.getenv("TTS_MODEL_ID", "local-tts"),
        )

    provider = TTSProvider(provider)

    if provider == TTSProvider.MOCK:
        return MockTTSGenerator(kwargs.get("output_root", "artifacts/audio"))

    if provider in {TTSProvider.LOCAL, TTSProvider.REMOTE}:
        raise RuntimeError(
            f"Provider '{provider.value}' is reserved for a concrete TTS adapter."
        )

    raise ValueError(f"Unsupported TTS provider: {provider}")


def get_tts_provider(provider: str | None = None, **kwargs):
    return create_tts_provider(
        provider or os.getenv("TTS_PROVIDER", "mock"),
        **kwargs,
    )


def get_tts_generator(provider: str | None = None, **kwargs):
    return get_tts_provider(provider, **kwargs)

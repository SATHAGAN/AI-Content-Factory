from __future__ import annotations

import os

from app.services.stt.base import SpeechToTextProvider
from app.services.stt.mock import MockSpeechToTextProvider
from app.services.stt.providers.faster_whisper import FasterWhisperProvider


def create_stt_provider(
    provider: str | None = None,
    *,
    model: str | None = None,
    device: str | None = None,
    compute_type: str | None = None,
    cpu_threads: int | None = None,
) -> SpeechToTextProvider:
    selected = (provider or os.getenv("STT_PROVIDER", "mock")).lower()

    if selected == "mock":
        return MockSpeechToTextProvider()

    if selected in {"faster-whisper", "faster_whisper", "local"}:
        return FasterWhisperProvider(
            model_name=model or os.getenv("STT_MODEL", "base"),
            device=device or os.getenv("STT_DEVICE", "cpu"),
            compute_type=compute_type or os.getenv("STT_COMPUTE_TYPE", "int8"),
            cpu_threads=cpu_threads,
        )

    raise ValueError(f"Unsupported STT provider: {selected}")

from __future__ import annotations

from pathlib import Path

from app.services.stt.base import SpeechToTextProvider
from app.services.stt.models import STTConfig, STTResult


class SpeechToTextService:
    def __init__(self, provider: SpeechToTextProvider):
        self.provider = provider

    def transcribe(
        self,
        audio_path: str,
        config: STTConfig | None = None,
    ) -> STTResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(audio_path)

        active_config = config or STTConfig()
        result = self.provider.transcribe(str(path), active_config)

        if active_config.word_timestamps and not result.words:
            raise ValueError(
                "STT provider did not return word timestamps while they were required"
            )

        return result

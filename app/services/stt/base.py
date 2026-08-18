from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.stt.models import STTConfig, STTResult


class SpeechToTextProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, config: STTConfig) -> STTResult:
        raise NotImplementedError

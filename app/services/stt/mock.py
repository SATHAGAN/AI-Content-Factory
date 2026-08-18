from __future__ import annotations

from pathlib import Path

from app.services.stt.base import SpeechToTextProvider
from app.services.stt.models import STTConfig, STTResult, STTSegment, STTWord


class MockSpeechToTextProvider(SpeechToTextProvider):
    """Deterministic provider used for tests and development."""

    def transcribe(self, audio_path: str, config: STTConfig) -> STTResult:
        if not Path(audio_path).is_file():
            raise FileNotFoundError(audio_path)

        words = (
            STTWord("This", 0.0, 0.35, 0.99),
            STTWord("is", 0.35, 0.55, 0.99),
            STTWord("a", 0.55, 0.68, 0.98),
            STTWord("test.", 0.68, 1.10, 0.99),
        )
        segment = STTSegment(
            text="This is a test.",
            start_seconds=0.0,
            end_seconds=1.10,
            words=words,
        )
        return STTResult(
            text=segment.text,
            language=config.language or "en",
            duration_seconds=1.10,
            segments=(segment,),
            words=words,
            provider="mock",
            model="mock",
            metadata={"source": audio_path},
        )

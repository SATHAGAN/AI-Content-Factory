from pathlib import Path

import pytest

from app.services.stt.mock import MockSpeechToTextProvider
from app.services.stt.models import STTConfig
from app.services.stt.service import SpeechToTextService


def test_mock_provider_returns_word_timestamps(tmp_path):
    audio = tmp_path / "voice.wav"
    audio.write_bytes(b"fake-audio")

    result = MockSpeechToTextProvider().transcribe(
        str(audio),
        STTConfig(word_timestamps=True),
    )

    assert result.provider == "mock"
    assert result.words
    assert result.words[0].start_seconds == 0.0
    assert result.words[-1].end_seconds > result.words[0].start_seconds


def test_service_requires_audio_file(tmp_path):
    service = SpeechToTextService(MockSpeechToTextProvider())
    with pytest.raises(FileNotFoundError):
        service.transcribe(str(tmp_path / "missing.wav"))


def test_service_rejects_provider_without_words(tmp_path):
    class NoWordProvider(MockSpeechToTextProvider):
        def transcribe(self, audio_path, config):
            result = super().transcribe(audio_path, config)
            from app.services.stt.models import STTResult
            return STTResult(
                text=result.text,
                language=result.language,
                duration_seconds=result.duration_seconds,
                segments=result.segments,
                words=(),
                provider=result.provider,
                model=result.model,
            )

    audio = tmp_path / "voice.wav"
    audio.write_bytes(b"fake-audio")
    service = SpeechToTextService(NoWordProvider())

    with pytest.raises(ValueError, match="word timestamps"):
        service.transcribe(
            str(audio),
            STTConfig(word_timestamps=True),
        )


def test_service_accepts_no_word_timestamp_mode(tmp_path):
    class NoWordProvider(MockSpeechToTextProvider):
        def transcribe(self, audio_path, config):
            result = super().transcribe(audio_path, config)
            from app.services.stt.models import STTResult
            return STTResult(
                text=result.text,
                language=result.language,
                duration_seconds=result.duration_seconds,
                segments=result.segments,
                words=(),
                provider=result.provider,
                model=result.model,
            )

    audio = tmp_path / "voice.wav"
    audio.write_bytes(b"fake-audio")
    result = SpeechToTextService(NoWordProvider()).transcribe(
        str(audio),
        STTConfig(word_timestamps=False),
    )
    assert result.words == ()

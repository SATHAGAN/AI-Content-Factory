from pathlib import Path

from app.services.audio.models import TTSRequest
from app.services.audio.synthetic import SyntheticTTS
from app.services.audio.validator import inspect_wav,validate_audio


def test_synthetic_tts_creates_valid_audio(tmp_path):
    path=SyntheticTTS().generate(TTSRequest(
        text="This is a test narration for our content factory.",
        output_path=str(tmp_path/"voice.wav"),
    ))
    metadata=inspect_wav(path)
    assert metadata.duration_seconds > 0
    assert validate_audio(metadata)==[]


def test_audio_validator_rejects_empty_duration(tmp_path):
    import wave
    path=tmp_path/"empty.wav"
    with wave.open(str(path),"wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
    metadata=inspect_wav(path)
    assert "Audio duration is too short" in validate_audio(metadata)

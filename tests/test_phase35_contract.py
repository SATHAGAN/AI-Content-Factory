from app.services.audio.models import TTSRequest
from app.services.audio.synthetic import SyntheticTTS
from app.services.audio.validator import inspect_wav,validate_audio
from app.services.avsync.models import check_sync


def test_audio_to_sync_contract(tmp_path):
    audio=SyntheticTTS().generate(TTSRequest(
        text="A short story begins in a colorful forest.",
        output_path=str(tmp_path/"voice.wav"),
    ))
    metadata=inspect_wav(audio)
    assert validate_audio(metadata)==[]

    report=check_sync(
        video_duration_seconds=metadata.duration_seconds,
        audio_duration_seconds=metadata.duration_seconds+0.05,
    )
    assert report.passed

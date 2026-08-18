from pathlib import Path

from app.services.tts.config import DEFAULT_TTS_PROFILES
from app.services.tts.benchmark import benchmark
from app.services.tts.synthetic import SyntheticTTSProfileProvider


def test_tts_profiles_are_dynamic():
    assert "english_narrator" in DEFAULT_TTS_PROFILES
    assert "english_story" in DEFAULT_TTS_PROFILES
    assert DEFAULT_TTS_PROFILES["english_story"].speaker=="Serena"


def test_tts_benchmark_contract(tmp_path):
    profile=DEFAULT_TTS_PROFILES["english_narrator"]
    result=benchmark(
        SyntheticTTSProfileProvider(),
        profile,
        "This is a short benchmark narration for our content factory.",
        str(tmp_path/"voice.wav"),
    )
    assert result.audio_duration_seconds > 0
    assert result.realtime_factor > 0
    assert result.validation_errors==()
    assert Path(result.output_path).is_file()

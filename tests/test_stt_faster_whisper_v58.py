import sys
from types import SimpleNamespace

from app.services.stt.factory import create_stt_provider
from app.services.stt.models import STTConfig
from app.services.stt.providers.faster_whisper import FasterWhisperProvider


def test_factory_defaults_to_mock():
    provider = create_stt_provider("mock")
    assert provider.__class__.__name__ == "MockSpeechToTextProvider"


def test_factory_creates_cpu_faster_whisper_without_loading_model():
    provider = create_stt_provider(
        "faster-whisper",
        model="base",
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
    )
    assert isinstance(provider, FasterWhisperProvider)
    assert provider.model_name == "base"
    assert provider.device == "cpu"
    assert provider.compute_type == "int8"


def test_faster_whisper_adapter_maps_segments_and_words(monkeypatch, tmp_path):
    audio = tmp_path / "voice.wav"
    audio.write_bytes(b"fake")

    class FakeModel:
        def transcribe(self, *args, **kwargs):
            words = [
                SimpleNamespace(
                    word=" Hello",
                    start=0.0,
                    end=0.4,
                    probability=0.98,
                ),
                SimpleNamespace(
                    word=" world",
                    start=0.4,
                    end=0.9,
                    probability=0.97,
                ),
            ]
            segment = SimpleNamespace(
                text=" Hello world",
                start=0.0,
                end=0.9,
                words=words,
            )
            return iter([segment]), SimpleNamespace(
                language="en",
                language_probability=0.99,
                duration=0.9,
            )

    provider = FasterWhisperProvider()
    provider._model = FakeModel()

    result = provider.transcribe(
        str(audio),
        STTConfig(language="en", word_timestamps=True),
    )

    assert result.provider == "faster-whisper"
    assert result.text == "Hello world"
    assert len(result.words) == 2
    assert result.words[1].start_seconds == 0.4
    assert result.language == "en"


def test_lazy_import_has_actionable_error(monkeypatch):
    provider = FasterWhisperProvider()
    original = sys.modules.pop("faster_whisper", None)
    monkeypatch.setitem(sys.modules, "faster_whisper", None)
    try:
        try:
            provider._load()
        except RuntimeError as exc:
            assert "faster-whisper is not installed" in str(exc)
    finally:
        if original is not None:
            sys.modules["faster_whisper"] = original
        else:
            sys.modules.pop("faster_whisper", None)

from __future__ import annotations

from pathlib import Path

from app.services.stt.base import SpeechToTextProvider
from app.services.stt.models import STTConfig, STTResult, STTSegment, STTWord


class FasterWhisperProvider(SpeechToTextProvider):
    """Optional local faster-whisper adapter.

    The dependency is imported lazily so the application can start without the
    package installed. This keeps the core test suite lightweight.
    """

    def __init__(
        self,
        model_name: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        cpu_threads: int | None = None,
    ):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.cpu_threads = cpu_threads
        self._model = None

    def _load(self):
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. Install it to use the local "
                "FasterWhisperProvider."
            ) from exc

        kwargs = {
            "device": self.device,
            "compute_type": self.compute_type,
        }
        if self.cpu_threads is not None:
            kwargs["cpu_threads"] = self.cpu_threads

        self._model = WhisperModel(self.model_name, **kwargs)
        return self._model

    def transcribe(self, audio_path: str, config: STTConfig) -> STTResult:
        if not Path(audio_path).is_file():
            raise FileNotFoundError(audio_path)

        model = self._load()
        segments_iter, info = model.transcribe(
            audio_path,
            language=config.language,
            word_timestamps=config.word_timestamps,
            vad_filter=config.vad_filter,
            temperature=config.temperature,
        )

        segments: list[STTSegment] = []
        words: list[STTWord] = []

        for raw_segment in segments_iter:
            segment_words = []
            for raw_word in (getattr(raw_segment, "words", None) or []):
                word = STTWord(
                    text=str(raw_word.word).strip(),
                    start_seconds=float(raw_word.start),
                    end_seconds=float(raw_word.end),
                    confidence=(
                        float(raw_word.probability)
                        if getattr(raw_word, "probability", None) is not None
                        else None
                    ),
                )
                if word.text:
                    segment_words.append(word)
                    words.append(word)

            segments.append(
                STTSegment(
                    text=str(raw_segment.text).strip(),
                    start_seconds=float(raw_segment.start),
                    end_seconds=float(raw_segment.end),
                    words=tuple(segment_words),
                )
            )

        text = " ".join(s.text for s in segments).strip()
        duration = float(getattr(info, "duration", 0.0) or 0.0) or None
        detected_language = getattr(info, "language", None) or config.language

        return STTResult(
            text=text,
            language=detected_language,
            duration_seconds=duration,
            segments=tuple(segments),
            words=tuple(words),
            provider="faster-whisper",
            model=self.model_name,
            metadata={
                "device": self.device,
                "compute_type": self.compute_type,
                "language_probability": getattr(
                    info, "language_probability", None
                ),
            },
        )

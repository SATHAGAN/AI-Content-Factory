from __future__ import annotations

from pathlib import Path

from app.services.tts.interface import TTSProviderBackend
from app.services.tts.models import TTSModelInfo, TTSRequest, TTSResult


class MockTTSProvider(TTSProviderBackend):
    def __init__(self, output_root: str = "artifacts/audio"):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def list_models(self) -> list[TTSModelInfo]:
        return [
            TTSModelInfo(
                model_id="mock-tts-v1",
                provider="mock",
                display_name="Mock TTS Generator",
                min_vram_gb=0,
                max_text_characters=10000,
                languages=("en", "ta"),
                voices=("default", "narrator", "child"),
            )
        ]

    def synthesize(self, request, output_path: str | None = None):
        model_id = getattr(request, "model", None) or "mock-tts-v1"
        if not self.supports(request):
            raise ValueError("TTS request is unsupported by the selected mock model")

        words = max(1, len(request.text.split()))
        speed = max(0.1, float(getattr(request, "speed", 1.0)))
        duration = max(0.5, words / (2.5 * speed))

        output = (
            Path(output_path)
            if output_path
            else self.output_root / getattr(request, "job_id", "legacy-job") / "voice.wav"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(
            (
                f"MOCK_TTS\ntext={request.text}\n"
                f"language={request.language}\nvoice={request.voice}\n"
                f"speed={speed}\n"
            ).encode("utf-8")
        )

        # Legacy callers receive the legacy-shaped result; new callers receive
        # the richer result contract.
        if not hasattr(request, "model"):
            from app.services.tts.interfaces import TTSResult as LegacyTTSResult
            return LegacyTTSResult(
                provider="mock",
                model_id=model_id,
                audio_path=str(output),
                duration_seconds=duration,
            )

        return TTSResult(
            provider="mock",
            model=model_id,
            audio_path=str(output),
            duration_seconds=duration,
            sample_rate=getattr(request, "sample_rate", 24000),
            language=request.language,
            voice=request.voice,
            metadata={"mock": True},
        )



class MockTTSGenerator(MockTTSProvider):
    """Legacy-compatible class name."""
    pass

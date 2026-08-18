from __future__ import annotations
from pathlib import Path
from app.services.providers.contracts import AudioArtifact


class MockTTSProvider:
    provider = "mock"

    def __init__(self, model_id: str = "mock-tts-v1"):
        self.model_id = model_id

    def synthesize(self, text: str, output_dir: str, voice: str | None = None) -> AudioArtifact:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        path = Path(output_dir) / "narration.wav"
        path.write_bytes(b"MOCK_AUDIO")
        duration = max(1.0, len(text.split()) / 2.5)
        return AudioArtifact(str(path), duration, self.provider, self.model_id, {"voice": voice})

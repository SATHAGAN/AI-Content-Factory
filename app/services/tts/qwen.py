from __future__ import annotations
import os
import subprocess
from pathlib import Path
from app.services.tts.interfaces import TTSRequest, TTSResult


class QwenTTSWorker:
    """Adapter for a separately deployed Qwen3-TTS worker."""

    def __init__(self, command: str | None = None, output_dir: str = "./data/generated_tts"):
        self.command = command or os.getenv("QWEN_TTS_COMMAND", "")
        self.output_dir = Path(output_dir)

    def synthesize(self, request: TTSRequest) -> TTSResult:
        if not self.command:
            raise RuntimeError("QWEN_TTS_COMMAND is not configured")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output = self.output_dir / "voice.wav"
        command = self.command.format(
            text=request.text.replace('"', '\\"'),
            language=request.language,
            voice=request.voice,
            speed=request.speed,
            output=str(output),
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "TTS inference failed")
        if not output.exists():
            raise RuntimeError("TTS worker completed without producing an audio artifact")

        return TTSResult(
            provider="qwen3-tts",
            model_id=os.getenv("QWEN_TTS_MODEL_ID", "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"),
            audio_path=str(output),
            duration_seconds=0.0,
        )

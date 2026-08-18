from __future__ import annotations

import os
from pathlib import Path


class LocalTTSProvider:
    """Optional local TTS adapter.

    The concrete engine is selected by TTS_ENGINE. This phase intentionally
    supports a command boundary so Coqui/Piper/Qwen3-TTS can be swapped in
    without changing the content pipeline.
    """

    provider="local-command"

    def __init__(self, command: str | None = None, model_id: str | None = None):
        self.command=command or os.getenv("TTS_COMMAND","")
        self.model_id=model_id or os.getenv("TTS_MODEL_ID","local-tts")

    def synthesize(self, request, output_path: str | None = None) -> dict:
        if not self.command:
            raise RuntimeError("TTS_COMMAND is not configured")
        output=Path(output_path or "artifacts/audio/local-tts.wav")
        output.parent.mkdir(parents=True,exist_ok=True)

        text_file=output.with_suffix(".txt")
        text_file.write_text(request.text,encoding="utf-8")
        command=self.command.format(
            text_file=str(text_file),
            output=str(output),
            language=request.language,
            voice=request.voice,
            speed=request.speed,
        )
        import subprocess
        result=subprocess.run(command,shell=True,capture_output=True,text=True,timeout=900)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-3000:] or "TTS command failed")

        return {
            "audio_path":str(output),
            "duration_seconds":0.0,
            "provider":self.provider,
            "model_id":self.model_id,
            "duration_needs_probe":True,
        }

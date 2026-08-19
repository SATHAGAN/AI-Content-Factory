from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import imageio_ffmpeg

from app.services.providers.contracts import AudioArtifact


class DemoTTSProvider:
    """Offline-safe narration provider for end-to-end validation.

    It uses Edge TTS when available, then falls back to a generated tone so the
    pipeline still produces a valid media artifact in a clean environment.
    """

    provider = "demo_tts"
    model_id = "edge-tts-with-tone-fallback"

    def __init__(self, voice: str = "en-US-AriaNeural"):
        self.voice = voice

    def synthesize(self, text: str, output_dir: str, voice: str | None = None) -> AudioArtifact:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / "narration.wav"
        selected_voice = voice or self.voice

        if text.strip():
            try:
                import edge_tts

                async def _save() -> None:
                    communicate = edge_tts.Communicate(text, selected_voice)
                    await communicate.save(str(output_path))

                asyncio.run(_save())
            except Exception:
                self._tone(text, output_path)
        else:
            self._tone("", output_path)

        duration = self._duration(output_path)
        return AudioArtifact(
            uri=str(output_path),
            duration_seconds=duration,
            provider=self.provider,
            model_id=self.model_id,
            metadata={"voice": selected_voice},
        )

    @staticmethod
    def _tone(text: str, output_path: Path) -> None:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        duration = max(1.0, min(8.0, 1.8 + len(text) / 35.0))
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=660:sample_rate=44100",
                "-t",
                f"{duration:.2f}",
                "-ac",
                "1",
                "-ar",
                "44100",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    @staticmethod
    def _duration(path: Path) -> float:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        probe = subprocess.run(
            [ffmpeg, "-i", str(path), "-f", "null", "-"],
            capture_output=True,
            text=True,
        )
        marker = "Duration: "
        text = probe.stderr
        if marker in text:
            value = text.split(marker, 1)[1].split(",", 1)[0].strip()
            hours, minutes, seconds = value.split(":")
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return 0.0

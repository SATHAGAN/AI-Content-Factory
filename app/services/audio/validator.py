from __future__ import annotations

import wave
from pathlib import Path

from app.services.audio.models import AudioMetadata


def inspect_wav(path: str) -> AudioMetadata:
    p=Path(path)
    if not p.is_file():
        raise FileNotFoundError(path)
    if p.stat().st_size == 0:
        raise ValueError("Audio file is empty")

    with wave.open(str(p),"rb") as wf:
        frames=wf.getnframes()
        rate=wf.getframerate()
        channels=wf.getnchannels()
        if rate <= 0:
            raise ValueError("Invalid WAV metadata")
        duration=frames/rate

    return AudioMetadata(
        path=str(p),
        duration_seconds=duration,
        sample_rate=rate,
        channels=channels,
        size_bytes=p.stat().st_size,
    )


def validate_audio(metadata: AudioMetadata, *, min_duration: float = 0.1) -> list[str]:
    errors=[]
    if metadata.duration_seconds < min_duration:
        errors.append("Audio duration is too short")
    if metadata.sample_rate < 16000:
        errors.append("Sample rate is below 16 kHz")
    if metadata.channels < 1:
        errors.append("Audio has no channels")
    return errors

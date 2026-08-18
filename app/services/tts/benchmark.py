from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from app.services.audio.models import TTSRequest
from app.services.audio.validator import inspect_wav,validate_audio


@dataclass(frozen=True)
class TTSBenchmarkResult:
    model_id: str
    profile_id: str
    elapsed_seconds: float
    audio_duration_seconds: float
    realtime_factor: float
    output_path: str
    validation_errors: tuple[str,...] = ()

    def to_dict(self):
        return {
            "model_id":self.model_id,
            "profile_id":self.profile_id,
            "elapsed_seconds":round(self.elapsed_seconds,3),
            "audio_duration_seconds":round(self.audio_duration_seconds,3),
            "realtime_factor":round(self.realtime_factor,3),
            "output_path":self.output_path,
            "validation_errors":list(self.validation_errors),
        }


def benchmark(provider, profile, text: str, output_path: str):
    start=time.perf_counter()
    path=provider.generate(
        TTSRequest(
            text=text,
            language=profile.language,
            output_path=output_path,
            sample_rate=profile.sample_rate,
        ),
        speaker=profile.speaker,
    )
    elapsed=time.perf_counter()-start
    metadata=inspect_wav(path)
    errors=validate_audio(metadata)
    return TTSBenchmarkResult(
        model_id=profile.model_id,
        profile_id=profile.profile_id,
        elapsed_seconds=elapsed,
        audio_duration_seconds=metadata.duration_seconds,
        realtime_factor=(
            elapsed/metadata.duration_seconds
            if metadata.duration_seconds else float("inf")
        ),
        output_path=path,
        validation_errors=tuple(errors),
    )

from __future__ import annotations

import math
import wave
from pathlib import Path

from app.services.audio.models import TTSRequest


class SyntheticTTS:
    """Deterministic WAV generator used for integration tests."""

    def generate(self, request: TTSRequest) -> str:
        output=Path(request.output_path)
        output.parent.mkdir(parents=True,exist_ok=True)

        # Duration scales with text length but remains bounded for tests.
        duration=max(0.5,min(5.0,len(request.text)/20))
        rate=request.sample_rate
        frames=int(duration*rate)

        with wave.open(str(output),"wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            for i in range(frames):
                sample=int(1200*math.sin(2*math.pi*440*i/rate))
                wf.writeframesraw(sample.to_bytes(2,"little",signed=True))
        return str(output)

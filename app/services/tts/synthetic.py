from __future__ import annotations

from app.services.audio.models import TTSRequest
from app.services.audio.synthetic import SyntheticTTS


class SyntheticTTSProfileProvider:
    def __init__(self):
        self.provider=SyntheticTTS()

    def generate(self, request, *, speaker=None):
        return self.provider.generate(request)

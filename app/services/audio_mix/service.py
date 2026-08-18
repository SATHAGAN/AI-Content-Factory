from app.services.audio_mix.ffmpeg import AudioMixEngine
from app.services.audio_mix.models import AudioMixRequest, AudioMixResult


class AudioMixService:
    def __init__(self, engine: AudioMixEngine | None = None):
        self.engine = engine or AudioMixEngine()

    def mix(self, request: AudioMixRequest) -> AudioMixResult:
        return self.engine.execute(request)

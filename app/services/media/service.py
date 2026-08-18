from __future__ import annotations

from app.services.media.ffmpeg import FFmpegMediaEngine
from app.services.media.models import MediaOperationRequest, MediaOperationResult


class MediaProcessingService:
    def __init__(self, engine: FFmpegMediaEngine | None = None):
        self.engine = engine or FFmpegMediaEngine()

    def process(self, request: MediaOperationRequest) -> MediaOperationResult:
        return self.engine.execute(request)

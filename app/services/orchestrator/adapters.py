from __future__ import annotations

from dataclasses import dataclass

from app.services.audio.models import TTSRequest
from app.services.timeline.models import SceneClip


@dataclass(frozen=True)
class GeneratedMedia:
    video_path: str
    duration_seconds: float


@dataclass(frozen=True)
class GeneratedAudio:
    audio_path: str
    duration_seconds: float


@dataclass(frozen=True)
class QAResult:
    ok: bool
    errors: tuple[str,...] = ()


class SceneVideoAdapter:
    def __init__(self, provider):
        self.provider=provider

    def generate_scene(self, *, scene, channel):
        return self.provider.generate_scene(scene=scene, channel=channel)


class SceneTTSAdapter:
    def __init__(self, provider):
        self.provider=provider

    def generate_scene_audio(self, *, scene, voice):
        request=TTSRequest(
            text=scene.narration,
            language=voice.language,
            output_path=f"artifacts/audio/{scene.scene_id}.wav",
        )
        return self.provider.generate(
            request,
            speaker=voice.speaker,
        )


class SceneQAAdapter:
    def __init__(self, validator):
        self.validator=validator

    def validate(self, *, scene, video, audio):
        errors=self.validator(scene=scene,video=video,audio=audio)
        return QAResult(ok=not errors,errors=tuple(errors))

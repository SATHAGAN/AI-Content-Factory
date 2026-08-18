from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.sync.audio_timing import AudioTimingPlanner
from app.services.video.factory import get_video_generator
from app.services.video.interfaces import VideoGenerationRequest
from app.services.tts.factory import get_tts_provider
from app.services.tts.interfaces import TTSRequest


@dataclass(frozen=True)
class SceneAsset:
    number: int
    video_path: str
    audio_path: str
    video_duration_seconds: float
    audio_duration_seconds: float
    timing_action: str
    speed_factor: float
    video_provider: str
    video_model_id: str
    tts_provider: str
    tts_model_id: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class SceneOrchestrator:
    """Generate one media bundle per planned scene.

    The orchestrator intentionally keeps video and speech providers behind
    interfaces, so changing models does not change the content pipeline.
    """

    def __init__(self, video=None, tts=None, timing=None):
        self.video = video or get_video_generator()
        self.tts = tts or get_tts_provider()
        self.timing = timing or AudioTimingPlanner()

    def generate_scene(
        self,
        scene: dict,
        *,
        language: str = "en",
        voice: str = "default",
        voice_speed: float = 1.0,
        width: int = 480,
        height: int = 832,
        fps: int = 16,
        seed: int | None = None,
    ) -> SceneAsset:
        number = int(scene.get("number", scene.get("order", 1)))
        target = float(scene["duration_seconds"])

        frames = max(1, round(target * fps))
        video = self.video.generate(VideoGenerationRequest(
            prompt=scene["visual_prompt"],
            width=width,
            height=height,
            frames=frames,
            fps=fps,
            seed=seed,
        ))
        audio = self.tts.synthesize(TTSRequest(
            text=scene.get("narration", ""),
            language=language,
            voice=voice,
            speed=voice_speed,
        ))

        timing = self.timing.decide(
            target_duration_seconds=video.duration_seconds,
            audio_duration_seconds=max(audio.duration_seconds, 0.001),
        )
        return SceneAsset(
            number=number,
            video_path=video.video_path,
            audio_path=audio.audio_path,
            video_duration_seconds=video.duration_seconds,
            audio_duration_seconds=audio.duration_seconds,
            timing_action=timing.action,
            speed_factor=timing.speed_factor,
            video_provider=video.provider,
            video_model_id=video.model_id,
            tts_provider=audio.provider,
            tts_model_id=audio.model_id,
        )

    def generate_plan(
        self,
        plan: dict,
        *,
        language: str = "en",
        voice: str = "default",
        voice_speed: float = 1.0,
        width: int = 480,
        height: int = 832,
        fps: int = 16,
        seed: int | None = None,
    ) -> dict:
        scenes = sorted(plan["scenes"], key=lambda x: x.get("number", x.get("order", 1)))
        assets = [
            self.generate_scene(
                scene,
                language=language,
                voice=voice,
                voice_speed=voice_speed,
                width=width,
                height=height,
                fps=fps,
                seed=None if seed is None else seed + i,
            )
            for i, scene in enumerate(scenes)
        ]
        return {
            "title": plan.get("title", ""),
            "target_duration_seconds": plan.get("target_duration_seconds"),
            "scene_count": len(assets),
            "assets": [asset.to_dict() for asset in assets],
            "status": "scene_assets_generated",
        }

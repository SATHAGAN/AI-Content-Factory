from __future__ import annotations
from app.services.video.factory import get_video_generator
from app.services.video.interfaces import VideoGenerationRequest
from app.services.tts.factory import get_tts_provider
from app.services.tts.interfaces import TTSRequest


def generate_scene(payload: dict) -> dict:
    scene = payload["scene"]
    video = get_video_generator().generate(
        VideoGenerationRequest(
            prompt=scene["visual_prompt"],
            width=payload.get("width", 480),
            height=payload.get("height", 832),
            frames=payload.get("frames", 97),
            fps=payload.get("fps", 16),
            seed=payload.get("seed"),
        )
    )
    audio = get_tts_provider().synthesize(
        TTSRequest(
            text=scene.get("narration", ""),
            language=payload.get("language", "en"),
            voice=payload.get("voice", "default"),
            speed=payload.get("voice_speed", 1.0),
        )
    )
    return {
        "scene_number": scene["number"],
        "video_path": video.video_path,
        "video_duration_seconds": video.duration_seconds,
        "video_provider": video.provider,
        "video_model_id": video.model_id,
        "audio_path": audio.audio_path,
        "audio_duration_seconds": audio.duration_seconds,
        "tts_provider": audio.provider,
        "tts_model_id": audio.model_id,
        "status": "generated",
    }

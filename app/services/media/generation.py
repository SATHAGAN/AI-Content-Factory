from __future__ import annotations

from pathlib import Path

from app.services.media.factory import get_video_provider
from app.services.tts.factory import get_tts_provider


class RealMediaGenerationService:
    """Provider-neutral scene media generation boundary."""

    def __init__(self, video=None, tts=None):
        self.video=video or get_video_provider()
        self.tts=tts or get_tts_provider()

    def generate_scene(self, scene: dict, output_dir: str, *, language="en", voice="default", speed=1.0, fps=16):
        directory=Path(output_dir)
        directory.mkdir(parents=True,exist_ok=True)
        number=int(scene["number"])

        from app.services.video.interfaces import VideoGenerationRequest
        from app.services.tts.interfaces import TTSRequest

        video_request=VideoGenerationRequest(
            prompt=scene["visual_prompt"],
            width=int(scene.get("width",480)),
            height=int(scene.get("height",832)),
            frames=max(1,round(float(scene["duration_seconds"])*fps)),
            fps=fps,
            seed=scene.get("seed"),
        )
        video_path=directory/f"scene_{number:03d}.mp4"
        video=self.video.generate(video_request,str(video_path))

        audio_request=TTSRequest(
            text=scene.get("narration",""),
            language=language,
            voice=voice,
            speed=speed,
        )
        audio_path=directory/f"scene_{number:03d}.wav"
        audio=self.tts.synthesize(audio_request,str(audio_path))

        return {
            "number":number,
            "video_path":video["video_path"] if isinstance(video,dict) else video.video_path,
            "audio_path":audio["audio_path"] if isinstance(audio,dict) else audio.audio_path,
            "video_duration_seconds":float(video.get("duration_seconds",0) if isinstance(video,dict) else video.duration_seconds),
            "audio_duration_seconds":float(audio.get("duration_seconds",0) if isinstance(audio,dict) else audio.duration_seconds),
            "video_provider":video.get("provider","") if isinstance(video,dict) else video.provider,
            "video_model_id":video.get("model_id","") if isinstance(video,dict) else video.model_id,
            "tts_provider":audio.get("provider","") if isinstance(audio,dict) else audio.provider,
            "tts_model_id":audio.get("model_id","") if isinstance(audio,dict) else audio.model_id,
        }

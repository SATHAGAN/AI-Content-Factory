from __future__ import annotations

from pathlib import Path
from app.services.rendering.ffmpeg_adapter import FFmpegAdapter


class AudioRenderService:
    def __init__(self, ffmpeg: FFmpegAdapter | None = None):
        self.ffmpeg=ffmpeg or FFmpegAdapter()

    def mux(self, video_path: str, audio_path: str, output_path: str) -> str:
        output=Path(output_path)
        output.parent.mkdir(parents=True,exist_ok=True)
        self.ffmpeg.run([
            "-i",video_path,
            "-i",audio_path,
            "-map","0:v:0",
            "-map","1:a:0",
            "-c:v","copy",
            "-c:a","aac",
            "-shortest",
            str(output),
        ])
        return str(output)

    def add_background_music(
        self,
        video_path: str,
        music_path: str,
        output_path: str,
        music_volume: float = 0.10,
    ) -> str:
        output=Path(output_path)
        output.parent.mkdir(parents=True,exist_ok=True)
        volume=max(0.0,min(1.0,music_volume))
        self.ffmpeg.run([
            "-i",video_path,
            "-stream_loop","-1","-i",music_path,
            "-filter_complex",
            f"[1:a]volume={volume}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map","0:v:0","-map","[a]",
            "-c:v","copy","-c:a","aac","-shortest",
            str(output),
        ])
        return str(output)

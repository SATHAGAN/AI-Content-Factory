from __future__ import annotations


def build_mux_plan(video_path: str, audio_path: str, output_path: str) -> list[str]:
    return [
        "ffmpeg",
        "-y",
        "-i",video_path,
        "-i",audio_path,
        "-map","0:v:0",
        "-map","1:a:0",
        "-c:v","copy",
        "-c:a","aac",
        "-shortest",
        output_path,
    ]

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class VideoBenchmarkConfig:
    model_id: str = "Wan-AI/Wan2.2-TI2V-5B"
    prompt: str = (
        "A cheerful animated child-friendly forest scene, a small fox "
        "walking beside a colorful stream, cinematic lighting, smooth motion"
    )
    width: int = 512
    height: int = 512
    frames: int = 40
    fps: int = 8
    output_path: str = "./benchmark_output/video.mp4"


@dataclass(frozen=True)
class TTSBenchmarkConfig:
    model_id: str = "Qwen/Qwen3-TTS"
    text: str = "Welcome to our first AI generated story."
    language: str = "English"
    output_path: str = "./benchmark_output/voice.wav"

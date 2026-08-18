from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class TTSProfile:
    profile_id: str
    model_id: str
    mode: str
    language: str
    speaker: str | None = None
    speed: float = 1.0
    sample_rate: int = 24000
    metadata: dict | None = None


DEFAULT_TTS_PROFILES = {
    "english_narrator": TTSProfile(
        profile_id="english_narrator",
        model_id="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        mode="custom_voice",
        language="English",
        speaker="Ryan",
    ),
    "english_story": TTSProfile(
        profile_id="english_story",
        model_id="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        mode="custom_voice",
        language="English",
        speaker="Serena",
    ),
    "voice_design": TTSProfile(
        profile_id="voice_design",
        model_id="Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        mode="voice_design",
        language="English",
    ),
}

from __future__ import annotations

import os

from app.services.providers.llm.mock import MockLLMProvider
from app.services.providers.tts.mock import MockTTSProvider
from app.services.providers.tts.qwen3 import Qwen3TTSProvider
from app.services.providers.video.mock import MockVideoProvider
from app.services.providers.video.wan_diffusers import WanDiffusersProvider


def get_video_provider():
    provider = os.getenv("VIDEO_PROVIDER", "mock")
    if provider == "mock":
        return MockVideoProvider(os.getenv("VIDEO_MODEL_ID", "mock-video-v1"))
    if provider in {"wan", "huggingface_diffusers"}:
        return WanDiffusersProvider()
    raise ValueError(f"Unsupported VIDEO_PROVIDER: {provider}")


def get_tts_provider():
    provider = os.getenv("TTS_PROVIDER", "mock")
    if provider == "mock":
        return MockTTSProvider(os.getenv("TTS_MODEL_ID", "mock-tts-v1"))
    if provider in {"qwen3", "qwen3_tts"}:
        return Qwen3TTSProvider()
    raise ValueError(f"Unsupported TTS_PROVIDER: {provider}")


def get_llm_provider():
    return MockLLMProvider()

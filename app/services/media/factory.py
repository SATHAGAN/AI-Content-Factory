from __future__ import annotations

import os

from app.services.video.mock import MockVideoGenerator
from app.services.media.providers.huggingface_diffusers import DiffusersVideoProvider


def get_video_provider():
    provider=os.getenv("VIDEO_PROVIDER","mock")
    if provider=="mock":
        return MockVideoGenerator()
    if provider in {"huggingface-diffusers","wan"}:
        return DiffusersVideoProvider(os.getenv("VIDEO_MODEL_ID"))
    raise ValueError(f"Unsupported VIDEO_PROVIDER: {provider}")

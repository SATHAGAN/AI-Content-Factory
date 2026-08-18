from __future__ import annotations
import os
from app.services.vlm.mock import MockVLM
from app.services.vlm.qwen3 import Qwen3VLWorker


def get_vlm():
    provider=os.getenv("VLM_PROVIDER","mock")
    if provider=="mock":
        return MockVLM()
    if provider=="qwen3-vl":
        return Qwen3VLWorker()
    raise ValueError(f"Unsupported VLM_PROVIDER: {provider}")

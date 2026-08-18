from __future__ import annotations

import time


class SyntheticInferenceProvider:
    """Deterministic provider for CI and architecture tests."""

    def __init__(self, latency_seconds: float = 0.001):
        self.latency_seconds=latency_seconds

    def generate(self, **kwargs):
        time.sleep(self.latency_seconds)
        return {
            "status":"ok",
            "frames":kwargs.get("frames"),
            "width":kwargs.get("width"),
            "height":kwargs.get("height"),
        }

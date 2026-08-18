from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "mock"
    base_url: str | None = None
    model_id: str = "mock-llm-v1"
    api_key: str | None = None
    temperature: float = 0.2
    max_tokens: int = 4096
    timeout_seconds: int = 300

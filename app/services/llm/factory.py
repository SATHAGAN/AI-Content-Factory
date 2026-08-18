from __future__ import annotations

import os

from app.services.content.planner import ContentPlanner
from app.services.llm.models import LLMConfig
from app.services.llm.planner_provider import StructuredLLMPlanner


def get_content_planner():
    provider=os.getenv("LLM_PROVIDER","mock")
    if provider=="mock":
        return ContentPlanner()
    if provider in {"openai-compatible","ollama","vllm"}:
        config=LLMConfig(
            provider=provider,
            base_url=os.getenv("LLM_BASE_URL"),
            model_id=os.getenv("LLM_MODEL_ID","local-model"),
            api_key=os.getenv("LLM_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE","0.2")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS","4096")),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS","300")),
        )
        return StructuredLLMPlanner(config)
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

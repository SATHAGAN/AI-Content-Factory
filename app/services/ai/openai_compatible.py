from __future__ import annotations

from typing import Any

import httpx

from app.services.ai.interfaces import GenerationResult, LLMProvider


class OpenAICompatibleLLM(LLMProvider):
    """LLM adapter for OpenAI-compatible inference servers.

    Works with vLLM and other compatible servers. The actual model is selected
    through configuration, so the application is not coupled to one vendor.
    """

    def __init__(
        self,
        base_url: str,
        model_id: str,
        api_key: str | None = None,
        timeout_seconds: float = 180.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        text = data["choices"][0]["message"]["content"]
        return GenerationResult(
            provider="openai-compatible",
            model_id=self.model_id,
            output={"text": text, "raw": data},
        )

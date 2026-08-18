from __future__ import annotations

import json
import urllib.error
import urllib.request

from app.services.llm.models import LLMConfig


class OpenAICompatibleClient:
    """Minimal dependency-free client for OpenAI-compatible local/remote servers.

    This works with servers exposing /chat/completions, such as a local
    inference server or a compatible cloud endpoint.
    """

    provider="openai-compatible"

    def __init__(self, config: LLMConfig):
        if not config.base_url:
            raise ValueError("base_url is required")
        self.config=config

    def generate(self, messages: list[dict], *, response_format: dict | None = None) -> dict:
        url=self.config.base_url.rstrip("/")
        if not url.endswith("/chat/completions"):
            url += "/chat/completions"

        payload={
            "model":self.config.model_id,
            "messages":messages,
            "temperature":self.config.temperature,
            "max_tokens":self.config.max_tokens,
        }
        if response_format:
            payload["response_format"]=response_format

        body=json.dumps(payload).encode("utf-8")
        request=urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type":"application/json",
                **({"Authorization":f"Bearer {self.config.api_key}"} if self.config.api_key else {}),
            },
        )
        try:
            with urllib.request.urlopen(request,timeout=self.config.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail=exc.read().decode("utf-8","ignore")
            raise RuntimeError(f"LLM server returned HTTP {exc.code}: {detail[-2000:]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Unable to reach LLM server: {exc}") from exc

    def text(self, system: str, user: str) -> str:
        data=self.generate([
            {"role":"system","content":system},
            {"role":"user","content":user},
        ])
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError,IndexError,TypeError) as exc:
            raise RuntimeError("LLM response did not contain choices[0].message.content") from exc

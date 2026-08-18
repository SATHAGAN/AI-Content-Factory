from __future__ import annotations

import json
import os
from typing import Any

import httpx

from app.services.judge.interfaces import JudgeInput, JudgeResult


class OllamaJudge:
    """Optional local multimodal judge adapter.

    The model is configurable; no specific model is hard-coded into the API.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_id: str | None = None,
        timeout_seconds: float = 180.0,
        pass_score: float = 0.75,
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model_id = model_id or os.getenv("JUDGE_MODEL_ID", "gemma3")
        self.timeout_seconds = timeout_seconds
        self.pass_score = pass_score

    def evaluate(self, item: JudgeInput) -> JudgeResult:
        prompt = f"""
You are a strict quality judge for an AI video production system.

Evaluate this scene:
SOURCE:
{item.source_text}

SCENE PROMPT:
{item.scene_prompt}

NARRATION:
{item.narration}

VISUAL DESCRIPTION:
{item.image_description or "not supplied"}

Return ONLY JSON:
{{
  "score": 0.0,
  "passed": false,
  "reasons": ["..."],
  "warnings": ["..."]
}}

Score dimensions:
- narrative consistency
- prompt/narration alignment
- visual plausibility when visual description is supplied
- originality and coherence
- age appropriateness
"""

        payload: dict[str, Any] = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

        try:
            parsed = json.loads(data["response"])
            score = float(parsed["score"])
            passed = bool(parsed.get("passed", score >= self.pass_score))
            reasons = [str(x) for x in parsed.get("reasons", [])]
            warnings = [str(x) for x in parsed.get("warnings", [])]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("Judge model did not return the required JSON contract") from exc

        return JudgeResult(
            provider="ollama",
            model_id=self.model_id,
            score=max(0.0, min(1.0, score)),
            passed=passed and score >= self.pass_score,
            reasons=reasons,
            warnings=warnings,
            raw=data,
        )

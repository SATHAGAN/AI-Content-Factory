from __future__ import annotations

from app.services.llm.models import LLMConfig
from app.services.llm.openai_compatible import OpenAICompatibleClient


def check_llm(config: LLMConfig) -> dict:
    client=OpenAICompatibleClient(config)
    try:
        response=client.generate([
            {"role":"system","content":"Reply with JSON only."},
            {"role":"user","content":"Return {\"ok\":true}"},
        ])
        return {
            "status":"ok",
            "provider":config.provider,
            "model_id":config.model_id,
            "response_shape_valid":bool(response.get("choices")),
        }
    except Exception as exc:
        return {
            "status":"error",
            "provider":config.provider,
            "model_id":config.model_id,
            "error":str(exc),
        }

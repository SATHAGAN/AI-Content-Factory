from app.services.ai.mock_llm import MockLLM
from app.services.ai.openai_compatible import OpenAICompatibleLLM


def get_llm_provider(
    provider: str = "mock",
    base_url: str | None = None,
    model_id: str | None = None,
    api_key: str | None = None,
):
    if provider == "mock":
        return MockLLM()
    if provider == "openai-compatible":
        if not base_url or not model_id:
            raise ValueError("base_url and model_id are required for openai-compatible provider")
        return OpenAICompatibleLLM(base_url, model_id, api_key)
    raise ValueError(f"Unsupported LLM provider: {provider}")

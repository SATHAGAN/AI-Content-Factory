import pytest


def test_mock_factory():
    from app.services.llm.factory import get_content_planner
    planner=get_content_planner()
    assert planner.__class__.__name__=="ContentPlanner"


def test_openai_compatible_factory_requires_server_at_runtime(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER","ollama")
    monkeypatch.setenv("LLM_BASE_URL","http://127.0.0.1:11434/v1")
    monkeypatch.setenv("LLM_MODEL_ID","test-model")
    from app.services.llm.factory import get_content_planner
    planner=get_content_planner()
    assert planner.__class__.__name__=="StructuredLLMPlanner"

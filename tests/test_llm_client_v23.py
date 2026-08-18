import json
from app.services.llm.models import LLMConfig
from app.services.llm.openai_compatible import OpenAICompatibleClient


class FakeResponse:
    def __init__(self,payload):
        self.payload=payload
    def read(self):
        return json.dumps(self.payload).encode()
    def __enter__(self): return self
    def __exit__(self,*args): pass


def test_client_builds_chat_completion_request(monkeypatch):
    captured={}
    def fake_urlopen(request,timeout):
        captured["url"]=request.full_url
        captured["body"]=json.loads(request.data.decode())
        return FakeResponse({"choices":[{"message":{"content":"hello"}}]})

    monkeypatch.setattr("urllib.request.urlopen",fake_urlopen)
    client=OpenAICompatibleClient(LLMConfig(
        base_url="http://localhost:11434/v1",
        model_id="test-model",
        api_key="secret",
    ))
    text=client.text("system","user")
    assert text=="hello"
    assert captured["url"].endswith("/v1/chat/completions")
    assert captured["body"]["model"]=="test-model"
    assert captured["body"]["messages"][1]["content"]=="user"

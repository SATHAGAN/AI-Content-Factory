# Phase 3 — Content Intelligence Engine

## Delivered

- Structured content planning service
- Provider-independent LLM interface
- Mock LLM for deterministic local testing
- OpenAI-compatible LLM adapter for vLLM/compatible inference servers
- JSON schema validation with Pydantic
- Dynamic language/category/audience/tone/duration/video-type inputs
- Character Bible structure
- Style Bible structure
- Scene Planner structure
- Scene-duration guardrail
- New `/api/v1/content/plan` endpoint
- Tests for structured planning and malformed output handling

## Model strategy

The application does not hard-code one model.

A cloud GPU can serve an open-weight model behind an OpenAI-compatible endpoint. A current candidate worth evaluating is Qwen3-30B-A3B-Instruct-2507, which is available on Hugging Face under Apache-2.0. NVIDIA Nemotron remains another model family to benchmark, but the newest larger Nemotron variants have substantial hardware requirements. This is why Phase 3 uses a provider interface instead of embedding a model directly.

## Local development

The default provider is `mock`.

To use a compatible server later:

```text
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=http://<gpu-worker>:8000
LLM_MODEL_ID=<served-model-id>
LLM_API_KEY=<optional>
```

The FastAPI process should not host the large model itself.

## Example plan request

```json
{
  "source_text": "A young fox gets lost in a forest and learns to ask for help.",
  "content_category": "kids story",
  "language": "en",
  "audience": "children 6-9",
  "tone": "warm and adventurous",
  "duration_seconds": 60,
  "video_type": "short"
}
```

The response is a structured plan that later phases can feed into:
- image/video generation
- TTS
- music/SFX
- subtitles
- rendering
- quality checks

## Deliberate limitation

This phase does not generate actual video or audio. It establishes the content intelligence contract first, so the media pipeline can consume stable structured data.

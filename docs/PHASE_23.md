# Phase 23 — Production LLM Integration Boundary

## Goal

Replace the deterministic content planner with a real open-source/local or remote Large Language Model (LLM) without changing the ContentPlan contract.

## Supported connection modes

```text
LLM_PROVIDER=mock
LLM_PROVIDER=ollama
LLM_PROVIDER=vllm
LLM_PROVIDER=openai-compatible
```

All non-mock modes use the same OpenAI-compatible `/chat/completions` protocol.

## Architecture

```text
Content Planner
      ↓
LLM Provider
      ↓
OpenAI-compatible client
      ↓
Local / remote inference server
      ↓
Structured JSON
      ↓
Pydantic validation
      ↓
ContentPlan
```

## Safety against malformed model output

The system now validates the model's JSON against the actual ContentPlan schema.

Invalid JSON or invalid fields are rejected instead of silently entering the generation pipeline.

## Why an OpenAI-compatible boundary?

It allows the application to switch between local inference servers and hosted inference without rewriting the planner.

The main application does not need to know whether the model runs:

- on the user's machine;
- on another GPU workstation;
- on a cloud GPU;
- behind a compatible inference API.

## Hardware

The current machine information supplied for this project is 8 GB RAM with no confirmed GPU. Therefore this phase does not assume that local inference is possible.

The provider boundary is designed so a stronger GPU machine can run the model while the web/API application remains unchanged.

## Testing

The suite tests:

- JSON validation
- Markdown-wrapped JSON
- malformed output rejection
- OpenAI-compatible request construction
- provider selection

No live LLM server is required for the tests.

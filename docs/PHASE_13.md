# Phase 13 — Background Generation Worker

## Delivered

The generation request is now actually consumed by a background worker.

### Pipeline state machine

```text
queued
  ↓
planning
  ↓
generating
  ↓
voice
  ↓
rendering
  ↓
media_qa
  ↓
ai_judge
  ↓
approval
```

The worker updates progress and stage independently from the browser request.

## Why this matters

A 5–10 minute video cannot safely be generated inside a normal HTTP request. The API accepts the job and the worker performs the long-running work.

## Current implementation

Phase 13 uses FastAPI BackgroundTasks and an in-process thread-safe registry for local development.

This is intentionally a replaceable boundary.

### Production evolution

For production:

```text
FastAPI
  ↓
Redis / durable queue
  ↓
GPU Worker
  ↓
PostgreSQL job state
```

The worker contract should remain the same.

## Current limitation

The stages are orchestration placeholders. They do not yet run the real GPU video model, TTS model, FFmpeg rendering, or AI judge.

Those providers will be connected behind these stages in the next phases.

## UI

The dashboard now polls the backend and displays live progress:

```text
Generating scenes   ███████░░░ 70%
```

This proves the complete asynchronous control path before expensive model integration.

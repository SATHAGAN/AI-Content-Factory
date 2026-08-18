# Phase 4 — GPU Worker, Job Queue & Media Pipeline Foundation

## Delivered

- Provider-independent asynchronous job contract
- In-memory development queue
- Priority handling
- Retry lifecycle
- Worker registry
- Tenant-scoped job API
- Render manifest
- Scene artifact model
- Sequential-scene validation
- Media pipeline contract
- FFmpeg runner abstraction
- First worker: render-manifest validation

## Architecture

```text
FastAPI
  |
  v
Job Manager
  |
  v
Queue abstraction
  |
  +--> LLM Worker
  +--> Scene Video Worker
  +--> TTS Worker
  +--> Render Worker
  +--> QA Worker
  +--> Publishing Worker
```

The current queue is intentionally in-memory for deterministic testing.

## Production replacement

The next infrastructure iteration should replace the in-memory queue with Redis + a durable worker system (for example Celery/RQ/Arq or a managed queue). The API contract should remain unchanged.

## GPU worker principle

The FastAPI server should not load a large video model.

Instead:

```text
API -> Queue -> GPU Worker -> Object Storage -> Job Result
```

A worker can claim one scene, generate it, upload the artifact, and mark the job complete. A failed scene can be retried without regenerating the entire video.

## Long-form video

Long videos are represented as a sequence of scene artifacts. Final rendering happens only after all required scene artifacts are present and validated.

## FFmpeg

FFmpeg is wrapped behind a service rather than scattered through the application. This allows local rendering and cloud worker rendering to use the same contract.

## Not yet included

- actual GPU model download
- actual text-to-video inference
- actual TTS inference
- Redis production queue
- cloud GPU provisioning
- real FFmpeg end-to-end render of generated clips
- YouTube/Instagram publishing

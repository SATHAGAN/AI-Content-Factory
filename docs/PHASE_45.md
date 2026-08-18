# Phase 45 — GPU Worker Architecture

## Goal

Separate the web/control application from expensive AI inference.

The user's i5 / 8 GB RAM computer should not be required to run every model.
The architecture now supports remote GPU workers.

## Architecture

```text
Web / API
   ↓
Persistent Job Store
   ↓
Task Queue
   ↓
Worker Scheduler
   ↓
┌───────────────┬────────────────┐
↓               ↓                ↓
GPU Worker 1    GPU Worker 2    CPU Worker
Video + TTS     Video + TTS     QA + FFmpeg
   ↓               ↓                ↓
   └───────────────┴────────────────┘
                   ↓
              Cloud Storage
```

## Worker capabilities

Workers advertise:

- video generation;
- TTS;
- QA;
- FFmpeg;
- VRAM;
- supported model IDs.

The scheduler matches tasks to capabilities.

## Model replacement

A task can request a preferred model:

```text
video-a
video-b
video-c
```

A compatible worker is selected without changing the production orchestrator.

## Queue

V1 uses an in-memory queue as a deterministic boundary.

Production can replace it with:

- Redis;
- RabbitMQ;
- Amazon Simple Queue Service (SQS);
- another durable queue.

## Health

Workers send heartbeats.

A stale worker can later be removed from scheduling and its running tasks recovered through Phase 44.

## Hardware reality

The current local machine profile (i5 CPU, 8 GB RAM, no specified GPU) should be treated as a control/development machine.

Actual video/TTS model inference should run on a suitable GPU worker.

The application architecture does not assume a specific GPU vendor.

## Testing

Worker registration, capability matching, model preference, queue priority, dispatch,
release, no-worker failure, and heartbeat staleness are tested.

No real GPU inference is claimed in this phase.

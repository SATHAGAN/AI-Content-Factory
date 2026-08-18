# Phase 44 — Persistent Jobs, Retry & Resume

## Goal

A 5–10 minute production must survive scene failures and worker interruptions without regenerating every scene.

## Persistent state

SQLite stores:

### Job

```text
job_id
channel_id
status
current_stage
target_duration
created_at
updated_at
error
metadata
```

### Scene

```text
job_id
scene_id
sequence
status
attempts
video_path
audio_path
error
metadata
```

## Resume behavior

```text
Scene 1  COMPLETED
Scene 2  COMPLETED
Scene 3  FAILED
Scene 4  COMPLETED
Scene 5  PENDING
```

Resume processes:

```text
Scene 3
Scene 5
```

Completed scenes are preserved.

## Worker interruption recovery

If a worker dies while a scene is marked `RUNNING`, the recovery manager changes it to `FAILED` with a retryable error.

## Retry policy

Default maximum attempts:

```text
3
```

This is configurable.

## Why this matters

Video generation can be expensive and slow. Regenerating a complete 10-minute video because one 8-second scene failed would waste compute.

The persistent scene state makes the architecture suitable for real GPU workers later.

## Production note

SQLite is appropriate for the V1 local/single-worker implementation.

When multiple GPU workers are introduced, the persistence layer should be replaceable with PostgreSQL and a proper queue/lease mechanism. The service boundary is intentionally kept separate so this migration does not require rewriting the generation pipeline.

# Phase 12 — Dashboard ↔ Backend Integration

## Delivered

The dashboard is no longer only a visual prototype.

It now has a real API client and can:

1. Create a project from the content form.
2. Persist the configuration in the backend workspace registry.
3. Enqueue a generation job.
4. Load the generation queue from the backend.
5. Refresh job state.
6. Keep organization-level access boundaries.

## Flow

```text
Dashboard
   ↓ POST /workspace/projects
Project configuration
   ↓ POST /workspace/generate
Generation Job
   ↓
Queue
   ↓
Future worker orchestration
```

## Important limitation

Phase 12 creates and queues the job, but it does NOT execute GPU generation yet.

The next worker phase must consume these jobs and update:

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
  ↓
scheduled
  ↓
publishing
  ↓
published
```

This separation is deliberate: the UI should never directly run a GPU model.

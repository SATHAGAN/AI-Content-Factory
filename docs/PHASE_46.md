# Phase 46 — Durable Queue & Worker Communication

## Goal

Replace the Phase 45 in-memory task queue with a persistent queue that can safely hand work to remote workers.

## Architecture

```text
Production Orchestrator
        ↓
 Persistent Job Store
        ↓
   Durable Queue
        ↓
 Worker polls task
        ↓
      Lease
        ↓
 ┌───────────────┐
 │ GPU Worker    │
 │ video / TTS   │
 └───────────────┘
        ↓
 heartbeat while working
        ↓
 ACK / FAIL
```

## Implemented

- Persistent SQLite task queue
- Priority ordering
- Worker leases
- Lease heartbeat
- Ownership checks
- Attempt limits
- Automatic requeue on failure before attempt limit
- Final failure after maximum attempts
- Worker-side queue client
- Integration with Phase 45 worker registry

## Why leases matter

If a worker disappears while holding a task, its lease eventually expires and the task becomes queued again.

This avoids permanently stuck jobs.

## Production migration path

SQLite is deliberately used for V1/local testing.

For multiple remote workers, the queue interface can later be backed by:

- Redis;
- Amazon Simple Queue Service (SQS);
- RabbitMQ;
- another durable queue.

The rest of the application should continue using the same queue contract.

## Testing

Tests cover:

- enqueue → claim → complete;
- priority;
- ownership;
- heartbeat;
- retry;
- maximum attempts;
- worker-client lifecycle;
- worker-registry integration.

No external queue service is required for the tests.

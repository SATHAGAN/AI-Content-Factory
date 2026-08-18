# Phase 28 — Dynamic Scheduling & Daily Production

## Goal

Move from a preview-only scheduler to a persistent, repeatable daily production planner.

## Flow

```text
Channel configuration
  ├─ daily_shorts_target
  ├─ daily_long_target
  ├─ language
  ├─ category
  ├─ platforms
  └─ scheduling windows
          ↓
DynamicSchedulePlanner
          ↓
DailyProductionScheduler
          ↓
GenerationJob records
          ↓
Worker queue / generation pipeline
          ↓
QA → render → publication (later phase)
```

## Idempotency

Every planned slot receives a deterministic `schedule_key`:

`daily:{channel}:{date}:{format}:{sequence}`

A unique database constraint prevents duplicate jobs if the scheduler runs twice. This makes it safe to execute from cron, CI, Kubernetes CronJob, or another scheduler.

## Configuration

The channel already exposes daily targets, so 5 Shorts / 2 long videos are only defaults—not hard-coded production limits. Channel `settings` can additionally define:

- `shorts_start_hour`
- `shorts_end_hour`
- `long_start_hour`
- `long_end_hour`
- `category`
- `content_profile_id`
- `platforms`
- `generation_priority`

## API

### Preview
`POST /api/v1/scheduling/preview`

Builds a schedule without persisting jobs.

### Run daily
`POST /api/v1/scheduling/run-daily`

Creates or reuses all daily generation jobs for one channel or the whole organization.

### List daily jobs
`GET /api/v1/scheduling/daily-jobs?day=YYYY-MM-DD`

Returns persistent daily generation jobs for the authenticated organization.

## Automation entry point

`scripts/run_daily_scheduler.py` is a deployment-friendly entry point. It can be invoked once per day by cron or a container scheduler.

## Deliberate boundary

Phase 28 schedules generation. It does not yet claim that content has been generated, approved, rendered, or published. Those are downstream state transitions and should remain explicit.

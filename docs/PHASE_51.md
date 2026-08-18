# Phase 51 — Automatic Media Repair Engine

## Goal

Do not immediately regenerate an entire scene when audio and video durations
do not match. Choose the smallest safe correction first.

## Decision hierarchy

```text
Sync mismatch
     ↓
Within tolerance?
 ┌───┴───┐
 YES     NO
  ↓       ↓
PASS   Repair Planner
          ↓
    ┌─────┼─────────────┐
    ↓     ↓             ↓
  TTS   Trim/Extend   Regenerate
  speed    video       media
    └─────┼─────────────┘
          ↓
       Re-check
          ↓
       PASS / FAIL
```

## Examples

### Audio is slightly too long

Prefer:

```text
Increase TTS speed
→ regenerate narration
→ remeasure duration
→ re-run sync gate
```

### Video is too long

Prefer:

```text
Trim video
→ remeasure
→ re-run sync gate
```

### Automatic adjustment is unsafe

Use:

```text
Regenerate audio/video
```

### Repeated failure

After the configured retry count:

```text
MANUAL_REVIEW
```

The system will never retry indefinitely.

## Safety

The executor is deliberately an adapter boundary. It does not silently modify
real media files until a concrete audio/video editing adapter is configured.

This prevents an incorrect repair from corrupting the source artifact.

## Future integration

The orchestration queue will create repair tasks and preserve:

- original artifact;
- repaired artifact;
- repair plan;
- attempt count;
- quality report;
- final decision.

This provides a full audit trail.

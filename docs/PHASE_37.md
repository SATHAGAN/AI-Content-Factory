# Phase 37 — Multi-Scene Timeline & Long-Form Assembly

## Goal

Make 5–10 minute videos reliable by generating short scenes independently and assembling them.

## Architecture

```text
Script
  ↓
Scene planner
  ↓
Scene 1 → Video + TTS
Scene 2 → Video + TTS
Scene 3 → Video + TTS
...
Scene N → Video + TTS
  ↓
Per-scene QA
  ↓
Timeline builder
  ↓
FFmpeg
  ↓
5–10 minute final video
```

## Dynamic scene length

The splitter supports arbitrary target scene duration.

Examples:

- 30 sec → 4 scenes at 8 sec target
- 60 sec → 8 scenes at 8 sec target
- 5 min → 38 scenes at 8 sec target
- 10 min → 75 scenes at 8 sec target

The final scene can be shorter.

## Merge modes

Two FFmpeg strategies are available:

1. **Re-encode concat** — safer when clips have different encoding parameters.
2. **Stream-copy concat** — faster when all clips are already compatible.

The merge service defaults to the safer re-encode plan.

## Limits

The current service caps one generated timeline at 600 seconds (10 minutes). This is a product safety boundary, not a model limitation.

## Important production behavior

Each scene remains independently recoverable.

If Scene 23 fails:

```text
Scenes 1–22 → keep
Scene 23     → regenerate
Scenes 24–75 → keep
```

Then the timeline is rebuilt.

This is one of the main reasons the scene-based architecture is preferable for the V1 long-video requirement.

# Phase 18 — Multi-Scene Narration Timeline & Synchronization

## Delivered

The rendering engine now builds one explicit narration timeline from all scene audio.

```text
Scene 1 audio → 0s
Scene 2 audio → 5s
Scene 3 audio → 10s
...
```

The timeline follows the exact video scene order.

## Sync decisions

For every scene:

- `keep` — audio and video are close enough
- `time_stretch` — small duration mismatch can be corrected
- `regenerate_or_recut` — mismatch is too large for automatic correction
- `inspect_source` — audio duration could not be measured

The system does not silently discard audio.

## Final pipeline

```text
Scene videos
    ↓
Video assembly
    ↓
Narration timeline
    ↓
Narration render
    ↓
Audio/video mux
    ↓
Optional music
    ↓
Optional subtitles
    ↓
Final video
```

## Important limitation

The timeline records the exact synchronization decisions. The current FFmpeg materializer concatenates tracks in timeline order; precise per-segment time-stretch filters should be enabled in the next media-quality phase after real FFprobe duration measurements are integrated.

## Why this matters

This is the foundation for the requested 5–10 minute videos: many short generated clips can now share a single, deterministic narration timeline.

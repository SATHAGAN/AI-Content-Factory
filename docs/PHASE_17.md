# Phase 17 — Final Video Rendering Engine

## Delivered

The project now has a dedicated rendering layer for assembling scene assets.

```text
Scene videos
    ↓
FFmpeg concat
    ↓
Assembled video
    ↓
Narration / music / subtitles
    ↓
Final video
```

## Important design choice

Phase 17 does **not** silently throw away scene narration.

If multiple scene audio files are supplied, the pipeline stops with an explicit error. This is intentional: narration must be placed on a proper timeline before muxing.

That timeline operation is the next rendering enhancement.

## Supported rendering operations

- scene ordering
- FFmpeg concatenation
- single-track audio muxing
- optional background music
- optional subtitle burn-in

## 5–10 minute videos

The architecture supports long videos by assembling many short scene clips. There is no assumption that the video model itself generates 5–10 minutes in one call.

## Current limitation

Multi-scene narration timeline assembly is intentionally deferred to the next phase so audio is never silently lost or incorrectly synchronized.

# Phase 55 — Voice-over and Background Music Mixing

## Goal

Give narration priority over background music while keeping the audio layer
configurable.

## Pipeline

```text
Voice-over ───────┐
                  ├──> Volume / Normalize
                  │
Music ────────────┤
                  ↓
             Audio Mixer
                  ↓
              AAC Audio
                  ↓
             Final Video
```

## Voice priority

When narration exists and music ducking is enabled:

- narration uses its configured volume;
- narration can be loudness-normalized;
- music is reduced to the configured ducked volume;
- both streams are mixed;
- the final render uses the mixed audio.

Default music volume is intentionally low.

## Dynamic controls

The future UI can expose:

- voice volume;
- music volume;
- ducked music volume;
- music ducking on/off;
- voice normalization;
- music normalization;
- sample rate.

These are configuration values rather than hard-coded decisions.

## Important limitation

This phase implements **static ducking**. It does not yet detect speech activity
and dynamically lower/raise music during individual speaking intervals.

A later phase can add sidechain compression or speech-activity-driven ducking.

## Testing

Tests use dry-run FFmpeg command generation and therefore do not require a
working codec installation.

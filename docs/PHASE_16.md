# Phase 16 — Scene Media Orchestration

## Goal

Turn the Phase 15 structured ContentPlan into independently generated scene assets.

## Pipeline

```text
ContentPlan
   ↓
Scene 1 ──→ Video provider
       └──→ TTS provider
       └──→ timing planner
   ↓
Scene 2 ──→ Video provider
       └──→ TTS provider
       └──→ timing planner
   ↓
...
   ↓
Scene media manifest
```

## Why scene-by-scene generation?

A 5–10 minute video is split into smaller scenes so that:

- a failed scene can be regenerated without recreating the whole video;
- different video models can be tested;
- voice-over can be checked per scene;
- scene duration can be corrected independently;
- later, parallel workers can generate scenes concurrently.

## Model switching

No video or TTS model is hard-coded into the orchestrator.

```text
VIDEO_PROVIDER=mock / wan / future-provider
TTS_PROVIDER=mock / qwen3-tts / future-provider
```

## Audio/video synchronization

Each scene is passed through `AudioTimingPlanner`.

Possible decisions:

- `keep`
- `time_stretch`
- `regenerate_or_recut`

Phase 16 records the decision. Actual audio time-stretch/muxing remains in the render phase.

## Manifest

The generated manifest records:

- scene number
- video path
- audio path
- media durations
- timing decision
- model/provider identifiers

This manifest becomes the input to the next render/assembly phase.

## Testing

Real Large Language Model (LLM), video model and text-to-speech (TTS) inference are not claimed as executed in the test environment. Provider interfaces are tested with deterministic fakes.

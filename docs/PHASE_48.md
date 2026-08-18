# Phase 48 — Dynamic Video Generation Provider Architecture

## Goal

Make video generation replaceable and configurable before connecting a real
open-source video model.

## Architecture

```text
Video Generation Service
          ↓
     Model Selector
          ↓
  ┌───────┼────────┐
  ↓       ↓        ↓
Local   Remote    Mock
GPU      GPU      Provider
  ↓       ↓
Model A Model B
```

## Dynamic selection

A request can specify:

- duration;
- resolution;
- frames per second (FPS);
- seed;
- model;
- prompt;
- negative prompt.

The selector checks:

- model enabled state;
- text-to-video support;
- maximum duration;
- worker video random-access memory (VRAM);
- provider compatibility.

## Why this matters

The final product should not depend permanently on one video model.

For example, a future configuration can expose:

```text
Video Model:
  [Model A ▼]

Available:
  Model A — 12 GB VRAM
  Model B — 16 GB VRAM
  Model C — 24 GB VRAM
```

Changing the model should not require changing:

- the job system;
- storage;
- publishing;
- quality assurance (QA);
- scheduling;
- the web application.

## Current limitation

Phase 48 intentionally does not pretend that the local machine can run a
large video-generation model. The user's current computer has no dedicated
video-processing graphics processing unit (GPU) information configured.

Real GPU adapters will be added after the provider-selection contract is stable.

## Testing

- model discovery;
- duration compatibility;
- worker VRAM filtering;
- explicit model selection;
- generation artifact creation;
- unknown-model failure;
- provider factory behavior.

No external model downloads or GPU are required for the tests.

## Backward compatibility

The phase retains the previous `VideoGenerationRequest`, `VideoGenerationResult`,
`get_video_provider()`, `get_video_generator()`, and `MockVideoGenerator`
integration points so older scene workers continue to operate while the new
selector is introduced.

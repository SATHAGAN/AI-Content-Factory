# Phase 43 — Production Orchestrator

## Goal

Connect the previously isolated components into one end-to-end production job.

## Pipeline

```text
Channel
   ↓
Content Source
   ↓
Research policy
   ↓
Scene Planner
   ↓
Scene Video generation
   +
Scene TTS
   ↓
Per-scene QA
   ↓
Timeline assembly
   ↓
Final video
```

## Provider independence

The orchestrator does not know which video model, Text-to-Speech (TTS) model,
Large Language Model (LLM), or storage implementation is used.

Each is injected as a provider/adapter.

This is required for your dynamic-model requirement.

Example:

```text
Video provider A → slow but high quality
Video provider B → fast
Video provider C → cheap

        ↓

Same orchestrator
```

## Failure behavior

A failure returns a structured `ProductionResult` with:

- job ID;
- failed stage;
- error;
- emitted pipeline event.

The next production-hardening phase should add persistent job state and
scene-level retry/resume so completed scenes survive a worker restart.

## Important status

The orchestrator is fully wired and tested with deterministic fake providers.

It does NOT claim real GPU video generation, real Qwen3-TTS inference, or real
FFmpeg execution in this unit-test environment.

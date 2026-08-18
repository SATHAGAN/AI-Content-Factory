# Phase 32 — V1 Model Selection & Runtime Profiles

## Why this phase exists

The architecture is complete, but real deployment requires concrete model choices.

The catalog keeps those choices configurable instead of scattering model IDs throughout the application.

## Current V1 recommendation

### Large Language Model (LLM)

`Qwen/Qwen3-30B-A3B-Instruct-2507`

Chosen for structured planning, multilingual content and strong general instruction following.

### Video

Primary:
`Wan-AI/Wan2.2-TI2V-5B`

Fallback:
`Wan-AI/Wan2.1-T2V-1.3B-Diffusers`

The 5B model is the preferred V1 quality candidate; the 1.3B model is retained for lower-resource integration tests.

### Text-to-Speech (TTS)

Qwen3-TTS family is selected as the V1 direction. The exact checkpoint should be pinned when the deployment environment is chosen.

### Quality Assurance (QA)

The software contract remains provider-independent. Deterministic QA is retained for smoke tests, while a Vision-Language Model (VLM) can be connected in the production worker.

## Hardware conclusion

The supplied development machine has 8 GB RAM and no confirmed Graphics Processing Unit (GPU) / Video Random Access Memory (VRAM).

Therefore:

```text
Development PC
    ↓
Web/API + scheduler + control panel
    ↓
Remote GPU worker
    ├── LLM
    ├── video
    ├── TTS
    └── VLM/QA
```

is the recommended V1 deployment shape.

## Important

Model catalog entries are configuration decisions, not proof that a model will fit a specific GPU. Actual resolution, quantization, batching and runtime determine memory requirements.

Before enabling production scheduling, benchmark one short scene on the selected GPU worker.

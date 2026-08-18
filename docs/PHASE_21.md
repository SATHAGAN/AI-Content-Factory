# Phase 21 — Real Vision-Language Model (VLM) Judge Boundary

## Delivered

The AI Judge now has a real multimodal inference boundary.

```text
Generated video
      ↓
Representative frame extraction
      ↓
Qwen3-VL / other VLM
      ↓
Structured scores
      ↓
Approve / Regenerate / Manual Review
```

## Model selection

The initial real adapter targets Qwen3-VL. Its current Hugging Face model family explicitly supports visual and video understanding.

For the user's local machine (8 GB RAM and no confirmed GPU), the application should not assume that a large model can run locally. The VLM worker is intentionally separate so it can run on a stronger machine or cloud GPU.

A small Qwen3-VL checkpoint can be selected through configuration without changing the pipeline.

## Frame sampling

The default judge path samples up to 12 frames at 1 frame per second.

These are configuration values, not hard-coded product behavior.

## Provider switching

```text
VLM_PROVIDER=mock
VLM_PROVIDER=qwen3-vl
```

The same interface can later support another Hugging Face model.

## Important limitation

The test suite uses `MockVLM`; no real Qwen3-VL inference is claimed in this build environment.

The real worker expects an external command that receives a prompt file and image-list file and returns JSON. This keeps the web application responsive and makes GPU inference replaceable.

## Why this architecture

A 5–10 minute video should not be sent blindly to a local model at full frame rate. Representative sampling reduces cost and latency while preserving enough evidence for scene-level quality checking.

A future enhancement can use adaptive sampling: increase frames for scenes where the first VLM pass detects continuity or temporal-quality uncertainty.

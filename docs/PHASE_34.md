# Phase 34 — Real GPU Video Benchmark Harness

## Purpose

This phase is intentionally different from the previous phases: it introduces the first **real inference execution path** while keeping it isolated from the main application.

The benchmark runs on a GPU worker, not the user's 8 GB RAM development PC.

## First test

Default configuration:

- Wan2.2-TI2V-5B
- 512 × 512
- 40 frames
- 8 frames/sec
- 5 seconds maximum
- one scene
- one output video

The purpose is to measure whether the selected GPU can actually execute the model before attempting long-form generation.

## Run on a compatible GPU worker

Install the pinned Python environment for the selected Diffusers/Wan runtime, then run:

```powershell
.\scripts\benchmark_video.ps1
```

Or:

```powershell
python -m app.services.real_benchmark.cli `
  --model Wan-AI/Wan2.2-TI2V-5B `
  --width 512 `
  --height 512 `
  --frames 40 `
  --fps 8
```

## What to record

The benchmark produces:

```text
video.mp4
video.benchmark.json
```

Record:

- GPU model
- GPU VRAM
- CUDA version
- PyTorch version
- Diffusers version
- model loading time
- generation time
- video duration
- output resolution
- peak VRAM
- success/failure
- visual quality

## Decision gate

Do not move to long-form generation until the 5-second test succeeds.

Then test:

```text
5 sec  → 10 sec → multiple scenes → 1 min → 5 min
```

## Current machine

The user's current machine has 8 GB RAM and no confirmed GPU, so this real benchmark must run on a remote/cloud GPU or another compatible GPU system.

The application remains runnable locally; only the inference worker moves to the GPU environment.

## TTS

The Qwen3-TTS provider remains a deliberate integration boundary. The exact checkpoint/runtime should be pinned after the video GPU benchmark and then benchmarked separately.

## Safety

The benchmark is not connected to automatic publishing. A generated test video cannot accidentally be uploaded to YouTube or Instagram.

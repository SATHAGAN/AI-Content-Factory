# Phase 33 — GPU Worker & Real-Model Benchmark Harness

## Why this phase exists

The next practical step after model selection is not blindly downloading models. We need a repeatable benchmark that tells us whether the selected inference environment is suitable.

## GPU worker architecture

```text
Main application
      ↓
GPU Worker Router
      ↓
┌──────────────┬──────────────┐
│ GPU Worker A │ GPU Worker B │
│ 24 GB        │ 48 GB        │
└──────────────┴──────────────┘
      ↓
LLM / Video / TTS / QA
```

Workers advertise:

- GPU name
- VRAM
- CUDA version
- backend
- supported tasks

The router chooses a compatible worker.

## Benchmark harness

The benchmark measures:

- warm-up runs
- measured runs
- latency
- success rate
- provider errors

This will allow us to compare real model/runtime combinations without changing the application.

## First real benchmark target

For the video model, benchmark a short scene first rather than a 5–10 minute video.

Recommended progression:

1. 5-second low-resolution scene
2. 5-second target-quality scene
3. 10-second scene
4. multiple-scene sequence
5. only then test longer videos

This is much safer than immediately attempting a long generation.

## Current hardware conclusion

The supplied PC has no confirmed GPU and 8 GB RAM. Therefore this benchmark harness is ready, but real Wan2.2 inference should be executed on a compatible GPU worker.

The official Wan2.2 TI2V-5B model card indicates 720p single-GPU inference requires at least 24 GB VRAM with offloading/CPU text encoder options; the repository also notes 80 GB VRAM for higher-memory configurations without those reductions. The model repository itself is about 34.2 GB. citeturn0search2turn0search6

For TTS, Qwen3-TTS currently has 0.6B and 1.7B checkpoints; the 0.6B Base checkpoint is about 2.52 GB on Hugging Face, making it a sensible first benchmark target. citeturn0search7turn0search9

## Production rule

Do not enable the automatic daily schedule until a real GPU-worker benchmark records:

- successful generation;
- acceptable latency;
- no out-of-memory failures;
- acceptable video quality;
- acceptable TTS quality;
- successful audio/video synchronization.

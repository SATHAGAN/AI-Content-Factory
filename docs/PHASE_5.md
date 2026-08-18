# Phase 5 — Video + Voice Generation Adapters

## Delivered

- Video generation provider interface
- Mock video provider for deterministic local testing
- Wan video worker adapter
- Text-to-speech provider interface
- Mock TTS provider
- Qwen3-TTS worker adapter
- Combined scene generation worker
- Scene-generation API
- Job-queue integration
- Tests for the complete scene generation contract

## Model direction

For the video layer, Wan2.1 is the first implementation target because its official repository provides a 1.3B T2V model intended for consumer GPUs and documents an 8.19 GB VRAM requirement for that model. It supports 480P generation and can be used as a practical first worker. citeturn0search4turn0search7

For higher-quality cloud GPU runs, Wan2.2 and LTX-family models can be benchmarked later. Hugging Face currently lists Wan2.2, Wan2.1, HunyuanVideo and LTX-family models among the active text-to-video ecosystem. citeturn0search0turn0search5

For voice, Qwen3-TTS provides open 0.6B and 1.7B checkpoints, multilingual generation and voice-control capabilities. The 0.6B CustomVoice model supports 10 major languages and is Apache-2.0 licensed. citeturn0search1turn0search2

## Important architecture decision

Do not run the large video model inside FastAPI.

Use:

```text
FastAPI
  ↓
Queue
  ↓
GPU Worker
  ├── Video model
  └── TTS model
  ↓
Object storage
  ↓
QA
  ↓
FFmpeg
```

This allows:
- multiple videos
- multiple channels
- independent scene retries
- model replacement
- cloud GPU scaling
- manual approval during early testing

## Current limitations

The real Wan and Qwen3-TTS models are not downloaded or executed by the test suite. Your current development machine does not have a suitable GPU, so the adapters are tested using deterministic mock providers.

The next phase should create the actual GPU-worker deployment, model download/configuration, artifact upload and real FFmpeg render test.

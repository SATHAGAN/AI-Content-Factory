# Phase 14 — Pluggable AI Model Provider Layer

## Delivered

The worker now has model-provider interfaces rather than hard-coded AI calls.

### Providers

```text
LLM
 └── MockLLMProvider

Video
 ├── MockVideoProvider
 └── WanDiffusersProvider

TTS
 ├── MockTTSProvider
 └── Qwen3TTSProvider
```

The provider is selected with environment configuration.

## Recommended initial models

### Video

Wan2.1 T2V 1.3B is kept as the initial optional adapter because the published model information describes the 1.3B T2V model as requiring about 8.19 GB of VRAM for its standard setup. This is important because the user's current machine has no GPU information supplied and therefore should not be assumed capable of local generation. citeturn0search14

### TTS

Qwen3-TTS 0.6B CustomVoice is used as the initial optional voice provider. Its Hugging Face model card describes multilingual synthesis and controllable voice/style behavior. citeturn0search4

The 0.6B Base checkpoint is also available for voice cloning and is about 2.52 GB of model repository size. citeturn0search0turn0search9

## Configuration

Example:

```env
VIDEO_PROVIDER=wan
VIDEO_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B-Diffusers
VIDEO_DEVICE=cuda

TTS_PROVIDER=qwen3
TTS_MODEL_ID=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
TTS_DEVICE=cuda
```

Development:

```env
VIDEO_PROVIDER=mock
TTS_PROVIDER=mock
```

## Why this architecture?

We do NOT want:

```text
if Wan:
   ...
if Qwen:
   ...
if another model:
   ...
```

spread throughout the application.

Instead:

```text
Pipeline
   ↓
Provider Interface
   ↓
Selected Model Adapter
```

That means the web UI can later expose model selection without rewriting the pipeline.

## Hardware note

The current CPU/RAM information is not enough to conclude that local AI video generation is practical. In particular, no GPU/VRAM was provided.

Therefore Phase 14 does not pretend the user's machine can run Wan locally.

The application can run in mock mode on CPU. Actual model execution should use a CUDA-capable GPU worker or a remote GPU service.

## What is NOT claimed

This phase does not claim that a 5–10 minute video can be generated in one model call.

The intended production approach remains:

```text
5–10 minute story
       ↓
Scene plan
       ↓
many short video clips
       ↓
TTS per scene / narration
       ↓
FFmpeg assembly
       ↓
final long video
```

That is the architecture we should use for long-form content.

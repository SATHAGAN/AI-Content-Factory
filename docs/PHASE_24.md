# Phase 24 — Real Video & TTS Provider Integration

## Delivered

The media layer now has real provider boundaries instead of requiring mock implementations.

```text
ContentPlan
   ↓
Media Generation Service
   ├── Video provider
   └── TTS provider
```

## Video

A local Hugging Face Diffusers adapter is included.

Default model configuration:

```text
VIDEO_PROVIDER=huggingface-diffusers
VIDEO_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B-Diffusers
```

The provider imports heavy libraries lazily, so the application can run without GPU packages when using another provider.

## TTS

The TTS layer now supports a local command boundary:

```text
TTS_PROVIDER=local-command
TTS_COMMAND=<your inference command>
TTS_MODEL_ID=<model>
```

This lets us connect Piper, Coqui, Qwen3-TTS, or another local engine without changing the generation service.

## Hardware reality

The user's current machine has 8 GB RAM and no confirmed GPU.

The local video provider may therefore be impractical on this machine. The architecture supports moving video/TTS inference to a GPU worker while the web application remains on the main machine/server.

## Important production behavior

The TTS command reports `duration_needs_probe=True` when it cannot provide duration metadata. Phase 19/18 FFprobe-based QA should measure the resulting audio before synchronization.

## Testing

The actual heavy model is not downloaded or executed during the test suite. Provider factories, lazy imports, media orchestration and file contracts are tested with deterministic fakes.

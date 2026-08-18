# Phase 49 — Dynamic Text-to-Speech Architecture

## Objective

Introduce a provider-neutral Text-to-Speech (TTS) layer so the content factory
can switch between local open-source models, remote inference, and a mock
provider without changing the orchestration layer.

## Flow

```text
Narration text
     ↓
TTS Request
     ↓
Model Selector
     ↓
Language + Voice + VRAM + Length
     ↓
Selected TTS Model
     ↓
Audio artifact
     ↓
Duration metadata
     ↓
Audio/Video synchronization
```

## Dynamic controls

The final application can expose:

- TTS provider
- TTS model
- Language
- Voice
- Speech speed
- Pitch
- Sample rate
- Worker GPU/VRAM profile

## Hardware strategy

The user's current machine has no dedicated GPU/VRAM configured. Therefore the
tests use a zero-VRAM mock profile and do not attempt to download or run a
large model locally.

A real open-source TTS model will be connected later through the same backend
contract. This keeps the system suitable for a cloud GPU worker while the web
application remains independent of the hardware.

## Synchronization

The generated result carries `duration_seconds`. The downstream media layer
can use that value to:

1. compare narration duration against the target scene duration;
2. extend/trim scene visuals;
3. detect major mismatch before rendering;
4. retry with adjusted speech speed when configured.

## Backward compatibility

`get_tts_provider()` and `get_tts_generator()` are provided so earlier media
orchestration code can migrate incrementally.

## Testing

Phase 49 tests cover:

- provider factory;
- model discovery;
- language and voice selection;
- VRAM filtering;
- audio artifact generation;
- duration metadata;
- invalid voice handling;
- environment-driven provider selection.

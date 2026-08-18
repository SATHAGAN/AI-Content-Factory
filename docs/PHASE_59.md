# Phase 59 — STT → Dynamic Caption Integration

## Goal

Connect the real Speech-to-Text result from Phase 58 directly to the subtitle
system from Phase 56.

## Complete flow

```text
Narration Audio
      ↓
Faster-Whisper
      ↓
STTResult
      ↓
Word Timestamps
      ↓
Caption Pipeline
      ↓
Subtitle Segmenter
      ↓
SRT / WebVTT
      ↓
Optional Burn-in
      ↓
Captioned Video
```

## Synchronization rule

The caption pipeline requires word timestamps.

If an STT provider returns a transcript but no word timestamps, the pipeline
fails safely instead of generating captions with guessed timings.

## Why this matters

This removes the manual transcript/timestamp requirement.

Once the voice-over is generated, captions can be created automatically.

## Current output options

The same STT result can produce:

1. standalone SRT;
2. standalone WebVTT;
3. a video with captions burned into the image.

## Provider independence

The caption layer does not know whether the transcript came from:

- Faster-Whisper;
- another local model;
- a future NVIDIA-backed inference service;
- a hosted Speech-to-Text provider.

It only consumes the standard STTResult contract.

## Next

The next major capability is the visual generation layer: turning a script
into scene prompts and connecting those prompts to selectable image/video
generation providers.

# Phase 35 — TTS, Audio Validation & Audio/Video Synchronization

## Delivered

The production pipeline now has an explicit audio contract.

```text
Narration
   ↓
TTS
   ↓
WAV
   ↓
Audio validation
   ↓
Duration analysis
   ↓
Video/audio synchronization
   ↓
FFmpeg mux plan
   ↓
Final video
```

## Audio validation

The validator checks:

- file exists;
- file is non-empty;
- duration;
- sample rate;
- channel count.

## Synchronization

A configurable tolerance is used.

Default:

```text
difference <= 150 ms → PASS
difference > 150 ms  → adjustment required
```

The timeline layer calculates a bounded playback adjustment rather than allowing arbitrary speed changes.

## FFmpeg

The mux layer creates an explicit FFmpeg command plan.

Actual execution remains a finalizer concern so that encoding settings can be changed independently.

## Real TTS

The architecture is ready for the real Qwen3-TTS provider, but this phase intentionally does not pretend that a real model was executed on the user's 8 GB / no-confirmed-GPU machine.

The first real benchmark should generate one short narration and compare:

- generation time;
- voice quality;
- pronunciation;
- language;
- duration accuracy;
- memory/VRAM.

## Why this matters for 5–10 minute videos

We now have the foundation to generate each scene independently:

```text
Scene 1 → video + narration
Scene 2 → video + narration
Scene 3 → video + narration
...
      ↓
Sync each scene
      ↓
Merge scenes
      ↓
Final 5–10 minute video
```

This is safer and more recoverable than asking one model to generate a 10-minute video in a single operation.

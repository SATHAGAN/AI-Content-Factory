# Phase 8 — Audio/Video Sync + Advanced QA + Subtitles

## Delivered

- Audio duration vs video duration analysis
- Automatic timing decision:
  - keep
  - time-stretch
  - regenerate/recut
- Silence-ratio detection
- Black-frame detection
- Frozen-frame detection
- Audio/video duration mismatch detection
- Subtitle (SRT) generation utility
- Manual approval state model
- Video QA API endpoint
- Real FFmpeg/FFprobe QA tests when available

## QA loop

```text
Generated video
      ↓
Media QA
      ├── duration
      ├── audio
      ├── silence
      ├── black frames
      └── frozen frames
      ↓
   PASS?
   /   \
 YES    NO
  |      |
  |      └── Retry / regenerate
  ↓
Manual approval (V1)
      ↓
Publishing
```

## Audio/video synchronization

The system does not blindly stretch narration.

It first measures the difference between target scene duration and narration duration.

Small mismatch:
- keep

Moderate mismatch:
- time-stretch within configured limits

Large mismatch:
- regenerate narration or recut the scene

This avoids unnatural voices caused by aggressive time stretching.

## What is intentionally NOT claimed

The system does not yet perform semantic visual quality assessment such as:
- "Is the character actually the same?"
- "Does the scene visually match the narration?"
- "Is this frame aesthetically good?"

Those require a vision-language model and should be added after the deterministic media QA is stable.

## V1 human approval

The user can inspect generated content before automatic publishing.

Once quality is proven, automatic approval/publishing can be enabled through configuration.

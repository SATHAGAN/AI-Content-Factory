# Phase 56 — Dynamic Subtitle and Caption Pipeline

## Goal

Turn transcript timestamps into readable captions and optionally burn them
into the final video.

## Pipeline

```text
Voice / Transcript
       ↓
Word timestamps
       ↓
Subtitle Segmenter
       ↓
Readable caption blocks
       ↓
SRT / WebVTT
       ↓
Optional FFmpeg burn-in
       ↓
Captioned Video
```

## Dynamic controls

The subtitle configuration supports:

- SRT or WebVTT;
- maximum characters per line;
- maximum lines;
- maximum subtitle duration;
- minimum subtitle duration;
- optional word timestamp retention.

These can later become per-channel settings.

## Why timestamped words matter

The system should not simply split a transcript by character count. Word
timestamps allow captions to follow the actual narration timing.

The architecture accepts word-level timestamps now. A later speech-to-text
adapter can produce those timestamps automatically from the generated
voice-over.

## Burn-in

Burn-in creates captions directly inside the video. We also preserve the
standalone subtitle artifact.

That gives the publishing layer a choice:

- upload the subtitle file where supported;
- burn captions into the video;
- do both.

## Important limitation

The current segmenter is deterministic and text-based. It does not yet perform
AI caption styling, animated word highlighting, karaoke captions, or speaker
identification.

Those can be added later without changing the transcript contract.

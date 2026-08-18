# Phase 7 — Artifact Storage, Rendering & Automated Video QA

## Delivered

- Artifact storage facade
- Local/Google Cloud Storage compatible artifact layer
- Secure upload path namespacing by organization
- File upload API
- FFmpeg scene concatenation
- Audio/video muxing
- Production render pipeline
- FFprobe-based video quality checks
- Resolution/fps/duration/audio validation
- Automated real FFmpeg tests when FFmpeg is installed

## Pipeline

```text
Generated scene clips
        ↓
Artifact Storage
        ↓
FFmpeg Concatenation
        ↓
Narration / Audio
        ↓
Audio + Video Mux
        ↓
FFprobe QA
        ↓
Final Artifact
```

## Why this matters

We do not want to publish a generated video just because the model returned a file.

The Quality Assurance (QA) stage checks:
- video stream exists
- duration is positive
- resolution is readable
- frame rate is readable
- audio exists when required
- FFprobe can parse the final file

More advanced checks will be added later:
- black-frame detection
- frozen-frame detection
- silent-audio detection
- speech/audio alignment
- subtitle alignment
- scene transition checks
- content safety checks
- visual consistency scoring

## Google Cloud Storage

The application already has a Google Cloud Storage adapter from earlier phases. Phase 7 adds the application-level artifact facade so generated media can move from workers into cloud storage without coupling the render pipeline to one storage provider.

## Important

The user's existing 5 TB Google storage can be used as the storage target, subject to the actual Google account/storage product and API access configuration. The application is designed so storage can be switched through configuration.

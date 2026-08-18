# Phase 52 — Real Media Processing Engine

## Goal

Implement the actual media operations required by the repair engine and final
rendering pipeline.

## Operations

The FFmpeg engine supports:

- trim video;
- extend video;
- adjust audio speed;
- normalize audio loudness;
- merge video and audio;
- extract audio.

## Safety

FFmpeg commands are constructed as argument lists, not shell command strings.

This means paths such as:

```text
my video; rm something.mp4
```

are passed as a single argument rather than being interpreted by a shell.

Outputs are created only under the requested filesystem path.

## Dry-run mode

The engine supports `dry_run=True`.

This is important for development and automated tests because command generation
can be validated without requiring FFmpeg or real media files.

## Audio speed

FFmpeg's `atempo` filter has a limited per-filter range. The implementation
builds a chain for larger speed changes instead of creating an invalid command.

## Important limitation

`-c copy` trimming/extension can be constrained by keyframes for some video
formats. A future production renderer can use re-encoding when frame-accurate
cuts are required.

Similarly, extending a video by looping the input is a simple deterministic
fallback. AI-generated scene continuation will be a separate capability.

## Next integration

Phase 51 repair plans can now be mapped to actual media operations, followed by
a Phase 50 synchronization check.

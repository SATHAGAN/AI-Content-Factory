# Phase 54 — Production Final Render Pipeline

## Goal

Create the final-render layer that turns ordered scene artifacts into one
video artifact.

## Pipeline

```text
Scene 1 ─┐
Scene 2 ─┤
Scene 3 ─┤
...      ├──> Render Manifest
Scene N ─┘          ↓
              Validate / Order
                    ↓
              FFmpeg Render
                    ↓
              Final MP4
                    ↓
             Quality Validation
```

## Manifest validation

Before rendering, the system verifies:

- at least one scene exists;
- scene order is deterministic;
- scene identifiers are unique;
- every scene has a positive duration;
- source video files exist;
- scene audio files exist when supplied;
- background music exists when enabled.

## 5–10 minute videos

There is no architectural 5–10 minute limit here. A final video can be built
from many short scenes.

For example:

```text
30 scenes × 20 seconds = 10 minutes
60 scenes × 10 seconds = 10 minutes
```

This is preferable for local generation because individual scenes can be
generated, validated, retried, and replaced independently.

## Important next integration

The current render engine establishes the assembly boundary. Voice-over,
subtitles, background music mixing, and per-scene audio need to be connected as
explicit FFmpeg filter stages rather than pretending that simple video
concatenation has already completed those operations.

This keeps the renderer testable and prevents accidental audio duplication.

## Performance

Long videos should be assembled from cached scene artifacts rather than
regenerating all scenes when one scene fails.

Future queue workers can render multiple independent scenes in parallel and
then perform one final assembly step.

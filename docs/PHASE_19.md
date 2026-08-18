# Phase 19 — Automated Media Quality Assurance

Phase 19 introduces deterministic media checks before the Artificial Intelligence (AI) judge or publishing stages.

## Flow

```text
Rendered scene
    ↓
FFprobe metadata
    ↓
Media QA
    ├── video stream present?
    ├── audio stream present?
    ├── duration within tolerance?
    ├── resolution acceptable?
    └── frame rate acceptable?
    ↓
PASS / REVIEW / FAIL
    ↓
Selective regeneration plan
```

## Selective regeneration

Hard media failures identify the exact scene numbers that should be regenerated.

Example:

```json
{
  "required": true,
  "scene_numbers": [3, 8],
  "reason_codes": ["duration_mismatch", "missing_audio"]
}
```

The whole 5–10 minute video therefore does not need to be recreated because one scene failed.

## Configurable thresholds

The QA class exposes:

- duration tolerance
- minimum width
- minimum height
- minimum frames per second
- whether audio is required

These can later be exposed in the web settings.

## Scope

This phase checks deterministic media properties. Semantic questions such as whether the generated image matches the script, whether a character is visually consistent, or whether the video is attractive belong to the AI judge layer.

# Phase 50 — Audio/Video Synchronization and Quality Gate

## Goal

Before automatic publishing, verify that narration and rendered video are
within a configurable timing tolerance.

## Pipeline

```text
Generated video ─────┐
                     ├──> Media Probe
Generated narration ─┘
                         ↓
                    Duration Data
                         ↓
                    Sync Analyzer
                         ↓
                 PASS / WARNING / FAIL
                         ↓
                    Quality Gate
                         ↓
             ┌───────────┴───────────┐
             ↓                       ↓
          Continue             Adjust / Retry
```

## Thresholds

Defaults:

- maximum allowed duration delta: 0.35 seconds;
- warning threshold: 0.15 seconds;
- minimum audio duration: 0.20 seconds;
- minimum video duration: 0.20 seconds.

These values are configuration, not hard-coded business rules.

## Important limitation

This phase checks **timeline/container synchronization**, not true
mouth-to-phoneme lip synchronization.

For example, a video and narration can both be 10 seconds long while the
character's mouth movements are still wrong.

A later quality-assurance phase can add model-backed checks such as:

- scene timing;
- speech activity detection;
- subtitle alignment;
- visual event timing;
- optional lip-sync scoring.

## Automatic publishing behavior

`SyncQualityGate` provides:

- `continue` for a clean pass;
- `adjust_timing` for a warning;
- `regenerate_or_adjust` for a failure.

The publishing pipeline should require `approved=True` before publishing.

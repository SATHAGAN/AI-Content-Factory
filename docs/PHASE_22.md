# Phase 22 — Self-Healing Generation & Bounded Regeneration

## Delivered

The system can now recover from a failed scene without rebuilding the entire video.

```text
Generate scene
      ↓
Media QA + AI Judge
      ↓
PASS ─────────────→ Continue
      │
      ↓ FAIL
Diagnose reason
      ↓
Rewrite prompt
      ↓
Regenerate scene
      ↓
QA + Judge again
      ↓
PASS? ── yes ──→ Continue
      │
      no
      ↓
Retry until max_attempts
      ↓
Manual review
```

## Bounded loop

The default controller allows two regeneration attempts.

This is configurable and prevents:

- infinite regeneration loops
- uncontrolled GPU usage
- endless failures caused by an unsuitable model

## Reason-aware prompt rewriting

Different failures produce different constraints:

- character inconsistency → preserve appearance
- narration mismatch → show the narrated action
- continuity → preserve setting/camera/state
- visual quality → simplify composition
- prompt alignment → follow requested subject/action
- safety → keep content age-appropriate

## Manual review

If the scene still fails after the maximum attempts, it is explicitly returned for manual review.

The controller does not pretend a failed scene is acceptable.

## Architecture

The generator and evaluator are injected interfaces. Therefore the recovery loop can use:

- any video provider
- any TTS provider
- any deterministic QA
- any VLM/AI Judge

without changing the recovery controller.

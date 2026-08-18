# Phase 20 — AI Judge

## Goal

Add a semantic quality gate after deterministic Media Quality Assurance (QA).

```text
Media QA
   ↓
AI Judge
   ├── prompt alignment
   ├── visual quality
   ├── character consistency
   ├── narration alignment
   ├── continuity
   └── content safety
   ↓
APPROVE / REGENERATE / MANUAL REVIEW
```

## Architecture

The judge is a provider interface boundary.

The current provider is a deterministic mock so the application can be tested without downloading a multimodal model.

The `build_judge_prompt` function defines the contract for a future vision-language model.

## Evidence

A real judge should receive:

- original scene plan
- generated video frames
- narration transcript or source narration
- Media QA report
- safety result
- optional previous-scene reference frames for continuity

The judge must not score based on assumptions when evidence is absent.

## Scoring

The default weighted criteria are:

| Criterion | Weight |
|---|---:|
| Prompt alignment | 30% |
| Visual quality | 20% |
| Character consistency | 15% |
| Narration alignment | 15% |
| Continuity | 10% |
| Content safety | 10% |

Threshold: 75/100.

All thresholds and weights are implementation data and can be made configurable later.

## Selective regeneration

The judge identifies exact scene numbers.

```text
Scene 1 → approve
Scene 2 → approve
Scene 3 → regenerate
Scene 4 → approve
```

Only Scene 3 needs to be sent back to the generation worker.

## Important limitation

The Phase 20 mock judge is NOT a real semantic model. It validates the interface and decision flow.

The next implementation should connect a real local/open-source vision-language model or a configured external provider, with frame sampling and evidence-based scoring.

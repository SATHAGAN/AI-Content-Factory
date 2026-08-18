# Phase 9 — Multimodal Quality Judge + Safety Gate

## Delivered

- Provider-independent multimodal judge interface
- Deterministic mock judge
- Optional local Ollama judge adapter
- Configurable judge model
- Basic pre-publish content-safety gate
- Quality decision engine
- Quality API
- Automatic approve/regenerate/block decisions
- Tests for judge, safety, decision logic and API

## Quality architecture

```text
Generated Scene
      ↓
Deterministic Media QA
      ↓
Safety Gate
      ↓
Multimodal Judge
      ↓
Quality Gate
 ┌────┼───────┐
 ↓    ↓       ↓
PASS RETRY   BLOCK
 ↓    ↓       ↓
Approve Regenerate Human/Safety Review
```

## Why two different QA layers?

Deterministic QA is good at measurable media problems:
- broken video
- missing audio
- black frames
- frozen frames
- duration mismatch

A multimodal model is needed for semantic problems:
- narration does not match the scene
- visual content is inconsistent with the prompt
- story coherence is weak
- the scene is visually implausible
- character/style consistency is poor

## Current model adapter

The optional Ollama adapter lets a local vision-language model perform the semantic judgment without coupling the system to one model vendor.

The actual model should be selected after benchmarking on the user's generated content. Do not hard-code one model into the workflow.

## Safety

The included regex safety gate is only a first defense layer. It should never be treated as a complete safety classifier.

The production workflow should eventually combine:
1. deterministic safety rules
2. model-based safety classifier
3. platform policy checks
4. human review for high-risk cases

## V1 operating mode

Recommended:

```text
Generate
  ↓
QA
  ↓
Judge
  ↓
If good → Manual approval
If bad  → Regenerate
If unsafe → Block
```

Only after several hundred successful generations should fully automatic publishing be enabled.

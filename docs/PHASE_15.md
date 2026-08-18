# Phase 15 — Content Intelligence & Scene Planning

## Delivered

The system now converts raw source text into a structured `ContentPlan`.

```text
Source / Transcript
        ↓
Content Planner
        ↓
Hook
Title
Summary
Characters
Scenes
Narration
Visual prompts
Continuity notes
Keywords
        ↓
Video + TTS pipeline
```

## Dynamic categories

The planner accepts category as data:

- Kids
- Educational
- Facts
- Motivation
- Creative
- General

New categories do not require pipeline changes.

## Scene architecture

Each scene contains:

- order
- duration
- visual prompt
- narration
- dialogue
- characters
- transition
- continuity notes

The sum of scene durations is designed to match the requested target duration.

## Character continuity

For recurring characters, a stable character record is created and its visual traits are added to every relevant scene prompt.

This is the foundation for consistent characters across multiple generated clips.

## LLM boundary

`LLMContentPlanner` accepts an optional JSON-generating model adapter.

The current default remains deterministic so tests and local development work without a large model.

A real local/open-source Large Language Model (LLM) can be plugged in later without changing downstream schemas.

## Important

Phase 15 does NOT claim the deterministic planner is equivalent to a production LLM. It establishes the contract and pipeline so the LLM can be swapped in safely.

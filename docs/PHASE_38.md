# Phase 38 — LLM Story & Scene Planner

## Goal

Convert a topic, transcript, or source text into a structured production plan that the video and TTS systems can consume.

## Input

The user can provide:

- a topic;
- a transcript;
- an article/source text;
- a custom script;
- future content gathered by an automated source.

## Output

```text
StoryPlan
 ├── title
 ├── hook
 ├── category
 ├── language
 ├── target duration
 └── scenes[]
      ├── narration
      ├── visual prompt
      ├── duration
      ├── subtitle
      ├── camera
      ├── motion
      └── music mood
```

## Full pipeline connection

```text
Topic / Transcript
        ↓
      LLM
        ↓
    StoryPlan
        ↓
     Scenes
        ↓
 ┌──────┴──────┐
 ↓             ↓
Video          TTS
 ↓             ↓
 └──────┬──────┘
        ↓
     Sync + QA
        ↓
    Timeline
        ↓
  Final 5–10 min
```

## Dynamic

The planner is not locked to a category, language, audience, duration, or scene count.

The same engine can produce:

- kids;
- educational;
- facts;
- motivation;
- general;
- future custom categories.

## Reliability

The LLM output is parsed and validated before entering the generation pipeline.

Invalid plans are rejected before expensive video or TTS generation begins.

## Important production rule

The LLM does not directly generate the final video. It generates a structured plan. This separation makes model replacement and debugging much easier.

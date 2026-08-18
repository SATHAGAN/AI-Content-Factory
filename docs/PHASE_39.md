# Phase 39 — Dynamic Content Source Engine

## Goal

Allow the factory to accept content from multiple sources without changing the generation pipeline.

## Supported source types

```text
Topic
Transcript
URL
File
AI-generated topic
```

### Topic

User supplies:

```text
"Why do dolphins sleep with one eye open?"
```

The system normalizes it into a content-generation request.

### Transcript

A user can paste an existing transcript.

### File

Text sources can be loaded from supported text formats such as TXT, Markdown, SubRip (SRT), WebVTT (VTT), and JSON.

### URL

The URL source is validated and represented as a source object. Actual web retrieval is intentionally separated into a connector layer so the application does not mix networking with content planning.

### AI-generated

The system can ask the configured LLM for a fresh topic.

## Dynamic metadata

Every source carries:

- language;
- category;
- audience;
- tone;
- target duration;
- custom metadata.

This is important for the future multi-channel system.

## Pipeline

```text
Manual topic ────────┐
Transcript ──────────┤
URL ─────────────────┤
File ────────────────┼→ Content Source
AI-generated topic ──┘
                         ↓
                   Scene Planner
                         ↓
                  Video + TTS + QA
```

## Next integration

The next layer should connect real URL/source retrieval and then feed the normalized source directly into the Phase 38 scene planner.

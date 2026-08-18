# Phase 57 — Speech-to-Text and Word Timestamp Abstraction

## Goal

Automatically convert generated narration into a transcript with timing
information that can feed Phase 56 subtitles.

## Pipeline

```text
Generated Audio
      ↓
Speech-to-Text Provider
      ↓
Transcript
      ↓
Segments + Word Timestamps
      ↓
Phase 56 Subtitle Segmenter
      ↓
SRT / WebVTT
```

## Provider architecture

The project does not hard-code one speech model.

The provider interface allows us to plug in:

- a local open-source speech model;
- a GPU inference server;
- a hosted Speech-to-Text API;
- a future higher-accuracy provider.

The initial implementation includes a deterministic mock provider for testing.

## Required contract

When `word_timestamps=True`, a provider must return word timestamps.

The service rejects providers that claim to support word timestamps but return
none. This prevents silently producing poorly synchronized captions.

## Why this is important for our dynamic system

The user will eventually be able to select a Speech-to-Text model from the UI,
for example:

```text
STT Provider
  ├── Local
  ├── Faster model
  ├── Higher-accuracy model
  └── Cloud provider
```

The rest of the content pipeline remains unchanged.

## Next integration

Connect the real local open-source Speech-to-Text provider and feed its word
timestamps directly into the subtitle service.

# Phase 42 — Multi-Channel Configuration

## Goal

Make channels first-class configuration objects so the factory can produce content for multiple independent channels.

## Channel configuration

Each channel owns:

- channel ID;
- display name;
- category;
- language;
- audience;
- tone;
- default duration;
- enabled platforms;
- voice profile;
- schedule metadata;
- custom metadata.

## Example

```text
Kids Stories
  category: kids
  voice: english_story
  duration: 5 min
  platforms: YouTube + Instagram

Daily Facts
  category: facts
  voice: english_narrator
  duration: 8 min
  platforms: YouTube + Instagram
```

## Job routing

A content job specifies:

- channel;
- source;
- target platforms;
- optional duration override.

The router resolves the channel configuration before generation.

## Why this matters

The generation engine remains channel-agnostic.

```text
                    Content Job
                        ↓
                  Channel Router
                        ↓
              ┌─────────┴─────────┐
              ↓                   ↓
         Kids Config         Facts Config
              ↓                   ↓
        Voice + Style         Voice + Style
              └─────────┬─────────┘
                        ↓
                 Same AI pipeline
```

## Platform rule

A job cannot publish to a platform that is not enabled for that channel.

This prevents accidental cross-channel publishing.

## Future scheduling

Schedule configuration is stored with the channel but automatic scheduling is intentionally not enabled yet.

The next phase should build the actual **production orchestration job** that takes:

```text
Channel + Source
      ↓
Research
      ↓
Scene planning
      ↓
Video + TTS
      ↓
QA
      ↓
Timeline
```

before publishing is connected.

# Phase 25 — Presentation, Branding & Platform Formats

## Delivered

The content factory now prepares presentation assets before final rendering.

### Subtitles

Narration is converted into a continuous SubRip Subtitle (SRT) timeline.

```text
Scene 1 narration → 00:00–00:05
Scene 2 narration → 00:05–00:10
...
```

### Background music

Music is optional and policy-controlled.

The default background volume is 10% so narration remains dominant.

### Thumbnails

A structured thumbnail plan is generated from:

- title
- hook
- target platform

The actual image generator remains provider-independent.

### Branding

Each channel can eventually have its own:

- name
- logo
- watermark
- intro
- outro

### Platform formats

The system now knows platform-specific output profiles:

- YouTube long-form — 16:9
- YouTube Shorts — 9:16
- Instagram Reels — 9:16
- Instagram Feed — 4:5

These are configuration records, not hard-coded generation behavior.

## Why this matters

The same content can later be rendered into multiple platform variants without regenerating the underlying story.

```text
One ContentPlan
      ↓
┌───────────────┬───────────────┐
│ YouTube       │ Instagram     │
│ 16:9          │ 9:16          │
└───────────────┴───────────────┘
```

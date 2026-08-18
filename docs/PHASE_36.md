# Phase 36 — Dynamic TTS / Voice System

## Model choice

The current V1 direction is the Qwen3-TTS family.

The official Qwen3-TTS collection currently includes 0.6B and 1.7B Base, CustomVoice, and VoiceDesign variants. The 0.6B Base checkpoint is listed at about 2.52 GB on Hugging Face. citeturn0search3turn0search5

For normal channel narration, V1 starts with:

`Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`

For future voice design:

`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`

The official Qwen demo exposes preset speakers including Aiden, Dylan, Eric, Ryan, Serena, Sohee, Uncle_fu and Vivian, and supports multiple languages. citeturn0search0turn0search9

## Dynamic voice profiles

Voices are not hard-coded into the pipeline.

A channel can select:

```text
profile_id
model
mode
language
speaker
speed
sample_rate
```

This means later we can add:

```text
Kids voice
Male narrator
Female narrator
Educational narrator
Story voice
Motivational voice
```

without rewriting the production engine.

## Benchmark

The benchmark measures:

- generation time;
- audio duration;
- realtime factor;
- WAV validity;
- sample rate;
- validation errors.

Realtime factor:

```text
generation_time / audio_duration
```

Lower is faster.

## Real inference

The real provider loads Qwen3-TTS lazily on the GPU worker through the official `qwen-tts` package. The package's official repository lists Python support through 3.13 and its required runtime dependencies. citeturn0search2

No model weights are downloaded during automated tests.

## Production behavior

The production pipeline will eventually:

```text
Script
 ↓
Select channel voice profile
 ↓
TTS
 ↓
Validate audio
 ↓
Sync against scene video
 ↓
Store audio
 ↓
Continue to final render
```

# Phase 58 — Real Local Faster-Whisper Speech-to-Text Provider

## Goal

Replace the mock-only Speech-to-Text path with a real local open-source
provider while keeping the provider interface dynamic.

The selected implementation is `faster-whisper`, a CTranslate2-based
implementation of Whisper. Its upstream documentation reports lower memory
usage and up to 4x speed improvements over the original Whisper
implementation in its benchmarks. citeturn0search0turn0search1

## Default for the current development machine

The project's default local profile is intentionally conservative:

```text
Model:        base
Device:       CPU
Compute type: int8
Word timing:  enabled
VAD:          enabled
```

The upstream project documents CPU `int8` operation and shows substantially
lower memory usage for its CPU int8 benchmark than float32. citeturn0search1

Because the current machine has 8 GB RAM and no confirmed dedicated GPU, this
is a safer starting point than automatically selecting a large model.

## Dynamic model selection

The factory supports:

```text
mock
faster-whisper
local
```

and the model can be changed without changing the application code.

Examples:

```text
tiny
base
small
medium
large-v3
```

The exact model choice can later be exposed in the web UI.

## GPU upgrade path

If an NVIDIA GPU is added later, the same adapter can use CUDA and an
appropriate compute type. Current upstream faster-whisper documentation notes
that GPU execution requires compatible NVIDIA CUDA/cuDNN libraries. citeturn0search1

## Why this architecture matters

The rest of the pipeline still consumes the same:

```text
STTResult
  ├── transcript
  ├── segments
  └── word timestamps
```

So changing the model does not require rewriting:

- subtitle generation;
- video rendering;
- synchronization checks;
- quality gates;
- publishing.

## Installation

The provider is optional at import time. To actually run it, install the
package:

```text
pip install faster-whisper
```

The upstream project documents this installation path. citeturn0search1

The test suite does not require downloading a model.

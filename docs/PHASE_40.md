# Phase 40 — Research & Source Verification Layer

## Goal

Prevent factual content from going directly from an LLM to video without a research/verification boundary.

## Research policy

By default, research is required for categories such as:

```text
facts
educational
science
history
news
finance
```

Creative categories can skip research by default:

```text
kids stories
motivation
fiction
```

The setting is still dynamic and can be explicitly overridden per request.

## Research packet

```text
ResearchPacket
 ├── topic
 ├── summary
 ├── claims[]
 │    ├── claim
 │    ├── source IDs
 │    ├── confidence
 │    └── importance
 └── sources[]
      ├── title
      ├── URL
      ├── publisher
      └── retrieval metadata
```

## Critical rule

A factual claim cannot enter the verified research packet without at least one supporting source reference.

This does not prove that the source itself is correct. It creates an explicit verification boundary that a future source-ranking and human-review layer can strengthen.

## Pipeline

```text
Topic / URL / Transcript
          ↓
    Source extraction
          ↓
      Research
          ↓
    Claims + Sources
          ↓
      LLM planner
          ↓
    Scene generation
```

## URL retrieval

Actual web retrieval is intentionally separated from the research contract. A production connector can use approved web/search tooling or another source provider, then populate `ResearchPacket`.

This separation allows source providers to change without rewriting the content-generation pipeline.

## Safety / quality gate

For factual channels, the production policy should eventually support:

- minimum number of independent sources;
- trusted-domain allowlists;
- source freshness requirements;
- claim-to-source traceability;
- confidence threshold;
- human approval for sensitive topics.

Those controls are not falsely marked as complete in this phase.

# Phase 47 — Cloud Storage Abstraction

## Goal

Store generated videos, audio, subtitles, thumbnails, research artifacts and
manifests outside the local worker filesystem.

## Canonical layout

```text
<channel>/<job>/<kind>/<filename>
```

Example:

```text
kids-stories/job-123/video/final.mp4
kids-stories/job-123/audio/scene-001.wav
kids-stories/job-123/subtitles/final.srt
kids-stories/job-123/research/research.json
kids-stories/job-123/manifest/timeline.json
```

## Providers

The storage contract supports:

- local storage;
- Google Drive;
- Google Cloud Storage.

The Google providers currently use a deterministic mock boundary in tests.
Real credentials and network access are intentionally not embedded into unit
tests.

## Why Google Drive is included

The project requirements mention approximately 5 TB of Google storage. Google
Drive and Google Cloud Storage are different products, so the application keeps
them as separate provider identities rather than pretending they are the same
thing.

## Security

Local storage rejects path traversal.

Cloud implementations should later add:

- OAuth/service-account credentials;
- least-privilege scopes;
- resumable uploads for large video files;
- checksum verification;
- retry with exponential backoff;
- upload encryption/configuration;
- lifecycle/retention policy.

## Next integration

The production orchestrator can upload the final video and intermediate
artifacts after successful rendering, while workers can download required
artifacts when resuming a job.

# Phase 30 — Cloud Storage & Production Deployment Boundary

## Delivered

The content factory now has a durable object-storage abstraction.

```text
Application
    ↓
ObjectStorage interface
    ├── Local storage
    └── Google Drive
```

The application can switch storage providers with configuration instead of rewriting the production pipeline.

## Google Drive

A Google Drive API v3 adapter is included.

Authentication is injected into the adapter; OAuth tokens are not stored in channel configuration or asset metadata.

Configure:

```text
STORAGE_PROVIDER=google-drive
GOOGLE_DRIVE_PARENT_FOLDER_ID=<folder-id>
```

The user's existing Google storage can therefore be used as the durable asset store, subject to the available Google Drive API quota and the storage plan/account.

## Asset organization

Assets use stable keys:

```text
channel/
  job/
    final_video/
    thumbnail/
    subtitle/
    source/
```

Temporary artifacts use separate classes:

```text
scene_video/
scene_audio/
frame/
intermediate/
```

This is important for lifecycle cleanup later.

## Deployment configuration

Production validation now prevents accidental deployment with:

- local-only storage
- disabled scheduler
- invalid worker count

## Health

A lightweight component health abstraction is included for:

- database
- storage
- LLM
- video
- TTS
- QA
- publishing

## Testing

The test suite covers:

- local storage round-trip
- safe asset keys
- lifecycle classification
- Google Drive adapter through an injected fake service
- production configuration validation
- component health

Real Google Drive uploads are intentionally not performed during automated tests.

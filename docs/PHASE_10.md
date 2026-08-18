# Phase 10 — Multi-Channel Publishing + Dynamic Scheduling

## Delivered

- Publishing provider abstraction
- Mock YouTube publisher
- YouTube Data API v3 publisher boundary
- Instagram/Meta Graph API publisher boundary
- Multi-channel publishing service
- Dynamic daily quotas
- Dynamic Shorts/long-video schedule planner
- Publication database model
- Publishing migration
- Publishing API
- Scheduling preview API
- Multi-platform tests

## Multi-channel design

A `Channel` is the logical content brand.

Each channel can have separate:

- YouTube account
- Instagram account
- content profile
- language
- approval mode
- Shorts target
- long-video target
- platform settings

The same generated asset can therefore be targeted to multiple channels without duplicating the generation pipeline.

## Dynamic daily volume

Nothing is hard-coded to 5 Shorts + 2 long videos.

Examples:

```text
Channel A:
5 Shorts + 2 long videos

Channel B:
10 Shorts + 1 long video

Channel C:
2 Shorts + 0 long videos
```

These are configuration values.

## YouTube

The official YouTube Data API uses `videos.insert` for uploads and supports metadata such as title, description, tags and privacy status. Resumable uploads are recommended for robust file transfer. Official documentation also states that uploads from unverified API projects created after July 28, 2020 are restricted to private viewing until the project passes the required audit. citeturn0search0turn0search2

This phase deliberately does not pretend that a real YouTube account is connected. The OAuth credentials must be supplied by the user and stored in a secret manager.

## Instagram

The Instagram publisher is intentionally a provider boundary until a credentialed Meta integration test is available. The application should use the official Meta Graph API flow for the connected professional account and must keep access tokens outside the database/application logs.

## V1 publishing safety

Recommended:

```text
Generate
  ↓
QA
  ↓
AI Judge
  ↓
Manual Approval
  ↓
Schedule
  ↓
Publish
```

Automatic publishing can be enabled later per channel.

## Important platform constraint

The scheduler controls our application-level publishing volume. It does not override platform-specific upload limits, account restrictions, API quotas, or review requirements.

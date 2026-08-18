# Phase 27 — YouTube & Instagram Publishing Boundary

## Delivered

The factory now has a platform publishing layer.

```text
Final video
   ↓
Channel
   ↓
Platform selection
   ├── YouTube
   └── Instagram
   ↓
Upload / Publish
   ↓
Result tracking
```

## YouTube

The provider is designed around the YouTube Data API v3 `videos.insert` upload flow with OAuth-authenticated service injection.

Current official YouTube requirements mean write operations require OAuth authorization. The YouTube upload scope is `https://www.googleapis.com/auth/youtube.upload`.

The provider supports:

- title
- description
- tags
- category
- privacy status
- scheduled publication timestamp
- resumable upload through `MediaFileUpload`

## Instagram

Instagram is represented as a separate authenticated client boundary. The application does not store or invent platform credentials.

The real Graph API client will be connected after the account/permission setup is established.

## Security

Tokens are not written into channel profiles.

The publishing providers accept authenticated clients/services from a secure credential layer.

## Important YouTube operational constraint

Official YouTube documentation states that videos uploaded through `videos.insert` by unverified API projects created after July 28, 2020 are restricted to private viewing until the project passes the required audit. This must be considered before automatic public publishing.

## Testing

- mock YouTube publishing
- mock Instagram publishing
- authentication-required behavior
- injected YouTube service
- multi-platform orchestration

Real platform uploads are intentionally not executed in automated tests.

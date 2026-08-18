# Phase 26 — Multi-Channel Management

## Delivered

The content factory now treats each channel as an independent configuration.

A channel can dynamically define:

- categories
- languages
- platforms
- brand profile
- model selection
- daily quotas
- other settings

## Example

```json
{
  "channel_id": "kids",
  "name": "Kids Stories",
  "categories": ["kids", "education"],
  "languages": ["en", "ta"],
  "platforms": ["youtube", "instagram"],
  "daily_quota": {
    "youtube_long": 2,
    "youtube_short": 5,
    "instagram_reel": 5
  }
}
```

Another channel can have completely different settings.

## Independent quotas

```text
Kids channel
  Shorts: 5/day

Facts channel
  Shorts: 10/day

Education channel
  Long videos: 2/day
```

Usage is tracked independently per channel and content type.

## Platform accounts

Each channel can connect separate platform accounts.

The registry intentionally stores an `account_key` abstraction rather than secrets. Real OAuth credentials/tokens should be stored in the secure credential layer in the publishing phase.

## Dynamic content

The orchestrator accepts the category, language and content type at job creation time. This keeps your original requirement: categories and publishing quantities can change later without rewriting the generation pipeline.

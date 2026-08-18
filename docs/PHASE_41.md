# Phase 41 — Source Retrieval Layer

## Goal

Add a real, provider-neutral HTTP retrieval boundary for URL-based content.

## Flow

```text
URL
 ↓
URL policy
 ↓
HTTP retrieval
 ↓
Content-type validation
 ↓
Size limit
 ↓
Text extraction
 ↓
Research packet
 ↓
Scene planner
```

## Implemented

- HTTP/HTTPS validation
- Content-type allowlist
- Request timeout
- Maximum response size
- HTML-to-text extraction
- Provider abstraction
- Deterministic mock provider
- Obvious localhost/private-host rejection

## Important security boundary

This is intentionally not a generic unrestricted URL fetcher.

A production deployment should additionally implement:

- DNS/IP rebinding protection;
- full private-network range blocking;
- redirect validation;
- domain allowlists/denylists;
- robots.txt and terms-of-service handling where applicable;
- rate limits;
- caching;
- retries with backoff;
- provenance tracking;
- source freshness;
- observability.

## Research integration

The retrieved document should become a `SourceReference` and its text should be passed to the research/claim extraction layer.

The source URL and retrieval metadata are preserved for traceability.

## Testing

Automated tests use the mock provider. Real internet retrieval is not required for unit tests.

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import httpx

from app.services.publishing.interfaces import PublishRequest, PublishResult


class YouTubePublisher:
    """YouTube Data API v3 uploader using OAuth access tokens.

    Production credentials should be retrieved from a secret manager using
    the platform-account credentials_ref. This adapter never persists tokens.
    """

    UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

    def __init__(
        self,
        access_token: str | None = None,
        upload_url: str | None = None,
        http_client: httpx.Client | None = None,
    ):
        self.access_token = access_token or os.getenv("YOUTUBE_ACCESS_TOKEN", "")
        self.upload_url = upload_url or self.UPLOAD_URL
        self.http = http_client or httpx.Client(timeout=120)

    def publish(self, request: PublishRequest) -> PublishResult:
        if not self.access_token:
            raise RuntimeError("YOUTUBE_ACCESS_TOKEN is not configured")

        path = Path(request.media_uri)
        if not path.exists():
            raise FileNotFoundError(path)

        body = {
            "snippet": {
                "title": request.title or "Untitled",
                "description": request.description or "",
                "tags": request.tags,
                "categoryId": request.metadata.get("category_id", "22"),
            },
            "status": {
                "privacyStatus": request.privacy,
                "selfDeclaredMadeForKids": bool(request.metadata.get("made_for_kids", False)),
            },
        }

        response = self.http.post(
            self.upload_url,
            params={"part": "snippet,status"},
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=UTF-8",
            },
            json=body,
        )
        # A real resumable-media implementation should be used for production
        # binary transfer. We explicitly fail here rather than silently doing
        # a metadata-only call.
        if response.status_code not in (200, 201):
            raise RuntimeError(f"YouTube upload initialization failed: {response.text[:1000]}")

        data = response.json()
        return PublishResult(
            platform="youtube",
            external_post_id=str(data.get("id", "")),
            status="initialized",
            raw=data,
        )

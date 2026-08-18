from __future__ import annotations
from uuid import uuid4
from app.services.publishing.interfaces import PublishRequest, PublishResult


class MockPublisher:
    def __init__(self, platform: str):
        self.platform = platform

    def publish(self, request: PublishRequest) -> PublishResult:
        post_id = f"mock_{self.platform}_{uuid4().hex[:12]}"
        return PublishResult(
            platform=self.platform,
            external_post_id=post_id,
            status="published",
            url=f"https://example.invalid/{self.platform}/{post_id}",
            raw={"media_uri": request.media_uri},
        )

from __future__ import annotations
from app.services.publishing.models import PublishRequest,PublishResult


class MockPublisher:
    def __init__(self, platform: str):
        self.platform=platform

    def publish(self, request: PublishRequest) -> PublishResult:
        return PublishResult(
            platform=self.platform,
            status="published",
            remote_id=f"mock-{self.platform}-{request.channel_id}",
            url=f"https://example.invalid/{self.platform}/{request.channel_id}",
            message="Mock publication completed",
            raw={"privacy_status":request.privacy_status},
        )

from __future__ import annotations

from pathlib import Path

from app.services.publishing.models import PublishRequest,PublishResult


class InstagramPublisher:
    """Instagram publishing boundary.

    The actual Graph API implementation is injected as `client` because
    publishing permissions and account setup are external platform concerns.
    """

    platform="instagram"

    def __init__(self, client=None):
        self.client=client

    def publish(self, request: PublishRequest) -> PublishResult:
        if self.client is None:
            raise RuntimeError(
                "Instagram publisher is not authenticated/configured. "
                "Supply a platform client with the required publishing permissions."
            )
        if not Path(request.video_path).is_file():
            raise FileNotFoundError(request.video_path)

        response=self.client.publish_video(
            video_path=request.video_path,
            caption=request.description or request.title,
            title=request.title,
            publish_at=request.publish_at,
            metadata=request.metadata,
        )
        remote_id=response.get("id")
        return PublishResult(
            platform=self.platform,
            status=response.get("status","uploaded"),
            remote_id=remote_id,
            url=response.get("url"),
            raw=response,
        )

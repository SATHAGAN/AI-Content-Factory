from __future__ import annotations

import os
from pathlib import Path

from app.services.publishing.models import PublishRequest,PublishResult


class YouTubePublisher:
    """YouTube Data API v3 upload boundary.

    OAuth credentials/tokens are deliberately supplied by the caller rather
    than persisted in this provider.
    """

    platform="youtube"

    def __init__(self, service=None, media_uploader=None):
        self.service=service
        self.media_uploader=media_uploader

    def publish(self, request: PublishRequest) -> PublishResult:
        if self.service is None:
            raise RuntimeError(
                "YouTube publisher is not authenticated. Supply an authorized "
                "YouTube Data API service client."
            )
        if not Path(request.video_path).is_file():
            raise FileNotFoundError(request.video_path)

        body={
            "snippet":{
                "title":request.title,
                "description":request.description,
                "tags":request.tags,
                "categoryId":str(request.metadata.get("category_id","22")),
            },
            "status":{
                "privacyStatus":request.privacy_status,
            },
        }
        if request.publish_at:
            body["status"]["publishAt"]=request.publish_at
            body["status"]["privacyStatus"]="private"

        media=self.service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=self._media_upload(request.video_path),
        )
        response=media.execute()
        video_id=response.get("id")
        return PublishResult(
            platform=self.platform,
            status="uploaded",
            remote_id=video_id,
            url=f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
            raw=response,
        )

    def _media_upload(self, path: str):
        if self.media_uploader is not None:
            return self.media_uploader(path)
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            raise RuntimeError(
                "Install google-api-python-client for YouTube publishing"
            ) from exc
        return MediaFileUpload(path,mimetype="video/*",resumable=True)

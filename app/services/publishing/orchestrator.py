from __future__ import annotations

from app.services.channels.orchestrator import MultiChannelOrchestrator
from app.services.publishing.factory import get_publisher
from app.services.publishing.models import PublishRequest


class PublishingOrchestrator:
    def __init__(self, channel_orchestrator, publisher_factory=get_publisher):
        self.channels=channel_orchestrator
        self.publisher_factory=publisher_factory

    def publish(self, job: dict, *, service=None, client=None, mock=False):
        channel_id=job["channel_id"]
        content_type=job["content_type"]
        self.channels.prepare_job(
            channel_id,
            category=job["category"],
            language=job["language"],
            content_type=content_type,
        )

        results=[]
        for platform in job["platforms"]:
            request=PublishRequest(
                channel_id=channel_id,
                platform=platform,
                video_path=job["video_path"],
                title=job["title"],
                description=job.get("description",""),
                tags=job.get("tags",[]),
                privacy_status=job.get("privacy_status","private"),
                publish_at=job.get("publish_at"),
                thumbnail_path=job.get("thumbnail_path"),
                metadata=job.get("metadata",{}),
            )
            publisher=self.publisher_factory(
                platform,service=service,client=client,mock=mock
            )
            results.append(publisher.publish(request))

        if results and all(r.status in {"published","uploaded","scheduled"} for r in results):
            self.channels.mark_published(job)
        return results

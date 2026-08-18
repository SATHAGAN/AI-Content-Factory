from __future__ import annotations

from app.services.channels.models import ChannelJob,Platform
from app.services.channels.registry import ChannelRegistry


class ChannelJobRouter:
    def __init__(self, registry: ChannelRegistry):
        self.registry=registry

    def resolve(self, job: ChannelJob) -> dict:
        channel=self.registry.get(job.channel_id)

        if not channel.enabled:
            raise ValueError(f"Channel is disabled: {channel.channel_id}")

        requested=set(job.target_platforms)
        configured=set(channel.platforms)
        unsupported=requested-configured

        if unsupported:
            names=", ".join(
                sorted(p.value if hasattr(p,"value") else str(p) for p in unsupported)
            )
            raise ValueError(
                f"Platforms not enabled for {channel.channel_id}: {names}"
            )

        return {
            "channel":channel,
            "duration_seconds":(
                job.duration_seconds
                if job.duration_seconds is not None
                else channel.default_duration_seconds
            ),
            "platforms":tuple(job.target_platforms),
            "voice":channel.voice,
            "category":channel.category,
            "language":channel.language,
            "audience":channel.audience,
            "tone":channel.tone,
        }

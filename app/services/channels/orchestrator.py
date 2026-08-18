from __future__ import annotations

from app.services.channels.content_policy import ChannelContentPolicy
from app.services.channels.quota import DailyQuotaManager
from app.services.channels.registry import ChannelRegistry


class MultiChannelOrchestrator:
    def __init__(self, registry=None, quota_manager=None, policy=None):
        self.registry=registry or ChannelRegistry()
        self.quota=quota_manager or DailyQuotaManager()
        self.policy=policy or ChannelContentPolicy()

    def prepare_job(self, channel_id: str, *, category: str, language: str, content_type: str) -> dict:
        channel=self.registry.get(channel_id)
        if not channel.enabled:
            raise ValueError(f"Channel '{channel_id}' is disabled")
        self.policy.validate(
            channel,category=category,language=language,content_type=content_type
        )
        if not self.quota.can_publish(channel_id,content_type,channel.daily_quota):
            raise RuntimeError(f"Daily quota reached for {channel_id}/{content_type}")

        platforms=[p for p in channel.platforms if p in {"youtube","instagram"}]
        return {
            "channel_id":channel.channel_id,
            "channel_name":channel.name,
            "category":category,
            "language":language,
            "content_type":content_type,
            "platforms":platforms,
            "brand_profile":channel.brand_profile,
            "models":channel.default_models,
        }

    def mark_published(self, job: dict) -> None:
        channel=self.registry.get(job["channel_id"])
        self.quota.record(job["channel_id"],job["content_type"],channel.daily_quota)

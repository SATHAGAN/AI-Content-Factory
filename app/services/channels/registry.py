
from __future__ import annotations

from app.services.channels.models import (
    ChannelConfig,
    ChannelPlatformAccount,
    ChannelProfile,
)


class ChannelRegistry:
    def __init__(self):
        self._channels={}
        self._accounts={}

    def add(self, channel) -> None:
        if channel.channel_id in self._channels:
            raise ValueError(f"Channel already exists: {channel.channel_id}")
        self._channels[channel.channel_id]=channel

    def update(self, channel) -> None:
        if channel.channel_id not in self._channels:
            raise KeyError(channel.channel_id)
        self._channels[channel.channel_id]=channel

    def get(self, channel_id: str):
        try:
            return self._channels[channel_id]
        except KeyError as exc:
            raise KeyError(f"Unknown channel: {channel_id}") from exc

    def list_enabled(self):
        return [c for c in self._channels.values() if c.enabled]

    def all(self):
        return list(self._channels.values())

    def connect_platform(self, account: ChannelPlatformAccount) -> None:
        channel=self.get(account.channel_id)
        platform=account.platform.lower()
        configured=[
            p.value if hasattr(p,"value") else str(p)
            for p in channel.platforms
        ]
        if platform not in configured:
            raise ValueError(
                f"Platform '{platform}' is not enabled for channel "
                f"'{account.channel_id}'"
            )
        self._accounts[(account.channel_id,platform)]=account

    def account(self, channel_id: str, platform: str) -> ChannelPlatformAccount:
        try:
            return self._accounts[(channel_id,platform.lower())]
        except KeyError as exc:
            raise KeyError(
                f"No connected account for {channel_id}/{platform}"
            ) from exc

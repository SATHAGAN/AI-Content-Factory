from __future__ import annotations


class ChannelContentPolicy:
    def validate(self, channel, *, category: str, language: str, content_type: str) -> None:
        if category not in channel.categories:
            raise ValueError(
                f"Category '{category}' is not enabled for channel '{channel.channel_id}'"
            )
        if language not in channel.languages:
            raise ValueError(
                f"Language '{language}' is not enabled for channel '{channel.channel_id}'"
            )
        if content_type not in channel.daily_quota:
            raise ValueError(f"Content type '{content_type}' has no configured quota")

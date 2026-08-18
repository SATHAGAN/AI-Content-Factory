from __future__ import annotations

from app.services.channels.models import ChannelConfig


def validate_channel(channel: ChannelConfig) -> list[str]:
    errors=[]

    if not channel.channel_id.strip():
        errors.append("channel_id is required")
    if not channel.name.strip():
        errors.append("name is required")
    if not channel.category.strip():
        errors.append("category is required")
    if not channel.language.strip():
        errors.append("language is required")
    if channel.default_duration_seconds <= 0:
        errors.append("default duration must be positive")
    if not channel.platforms:
        errors.append("at least one platform is required")
    if not channel.voice.profile_id.strip():
        errors.append("voice profile is required")
    if channel.voice.speed <= 0:
        errors.append("voice speed must be positive")

    return errors

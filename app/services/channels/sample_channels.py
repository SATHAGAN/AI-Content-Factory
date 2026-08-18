from app.services.channels.models import ChannelConfig,Platform,VoiceConfig


def sample_channels():
    return [
        ChannelConfig(
            channel_id="kids-stories",
            name="Kids Stories",
            category="kids",
            language="English",
            audience="children",
            tone="warm and playful",
            default_duration_seconds=300,
            platforms=(Platform.YOUTUBE,Platform.INSTAGRAM),
            voice=VoiceConfig(
                profile_id="english_story",
                speaker="Serena",
            ),
            schedule={"enabled":False,"youtube":2,"instagram":5},
        ),
        ChannelConfig(
            channel_id="daily-facts",
            name="Daily Facts",
            category="facts",
            language="English",
            audience="general",
            tone="curious and educational",
            default_duration_seconds=480,
            platforms=(Platform.YOUTUBE,Platform.INSTAGRAM),
            voice=VoiceConfig(
                profile_id="english_narrator",
                speaker="Ryan",
            ),
            schedule={"enabled":False,"youtube":1,"instagram":5},
        ),
    ]

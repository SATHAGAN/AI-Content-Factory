from app.services.channels.models import ChannelProfile
from app.services.channels.registry import ChannelRegistry
from app.services.channels.orchestrator import MultiChannelOrchestrator
from app.services.publishing.orchestrator import PublishingOrchestrator


def test_orchestrator_publishes_to_all_enabled_platforms(tmp_path):
    video=tmp_path/"video.mp4"; video.write_bytes(b"video")
    registry=ChannelRegistry()
    registry.add(ChannelProfile(
        channel_id="kids",name="Kids",categories=["kids"],languages=["en"],
        platforms=["youtube","instagram"],
        daily_quota={"youtube_short":2},
    ))
    channels=MultiChannelOrchestrator(registry)
    publisher=PublishingOrchestrator(channels)

    results=publisher.publish({
        "channel_id":"kids",
        "category":"kids",
        "language":"en",
        "content_type":"youtube_short",
        "platforms":["youtube","instagram"],
        "video_path":str(video),
        "title":"Test",
    },mock=True)

    assert len(results)==2
    assert {r.platform for r in results}=={"youtube","instagram"}

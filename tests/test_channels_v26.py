import pytest

from app.services.channels.models import ChannelProfile,ChannelPlatformAccount
from app.services.channels.registry import ChannelRegistry
from app.services.channels.orchestrator import MultiChannelOrchestrator


def channel(cid,name,categories,quota):
    return ChannelProfile(
        channel_id=cid,name=name,categories=categories,
        languages=["en","ta"],platforms=["youtube","instagram"],
        daily_quota=quota,
    )


def test_multiple_channels_are_independent():
    registry=ChannelRegistry()
    registry.add(channel("kids","Kids",["kids"],{"youtube_short":2}))
    registry.add(channel("facts","Facts",["facts"],{"youtube_short":1}))
    orch=MultiChannelOrchestrator(registry)

    a=orch.prepare_job("kids",category="kids",language="en",content_type="youtube_short")
    b=orch.prepare_job("facts",category="facts",language="en",content_type="youtube_short")
    assert a["channel_id"]=="kids"
    assert b["channel_id"]=="facts"

    orch.mark_published(a)
    orch.mark_published(b)
    assert registry.get("kids").daily_quota["youtube_short"]==2


def test_quota_is_enforced():
    registry=ChannelRegistry()
    registry.add(channel("facts","Facts",["facts"],{"youtube_short":1}))
    orch=MultiChannelOrchestrator(registry)
    job=orch.prepare_job("facts",category="facts",language="en",content_type="youtube_short")
    orch.mark_published(job)
    with pytest.raises(RuntimeError):
        orch.prepare_job("facts",category="facts",language="en",content_type="youtube_short")


def test_category_and_language_are_dynamic():
    registry=ChannelRegistry()
    registry.add(channel("edu","Education",["education"],{"youtube_long":2}))
    orch=MultiChannelOrchestrator(registry)
    with pytest.raises(ValueError):
        orch.prepare_job("edu",category="facts",language="en",content_type="youtube_long")
    with pytest.raises(ValueError):
        orch.prepare_job("edu",category="education",language="fr",content_type="youtube_long")


def test_platform_account_must_be_enabled_for_channel():
    registry=ChannelRegistry()
    registry.add(channel("x","X",["general"],{"youtube_long":1}))
    registry.connect_platform(ChannelPlatformAccount("x","youtube","yt-account"))
    assert registry.account("x","youtube").account_key=="yt-account"
    with pytest.raises(ValueError):
        registry.connect_platform(ChannelPlatformAccount("x","tiktok","bad"))

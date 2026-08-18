import pytest

from app.services.channels.models import (
    ChannelConfig,ChannelJob,Platform,VoiceConfig
)
from app.services.channels.registry import ChannelRegistry
from app.services.channels.validation import validate_channel
from app.services.channels.job_router import ChannelJobRouter


def make_channel(channel_id="facts",enabled=True):
    return ChannelConfig(
        channel_id=channel_id,
        name="Facts",
        category="facts",
        language="English",
        audience="general",
        tone="educational",
        default_duration_seconds=300,
        platforms=(Platform.YOUTUBE,Platform.INSTAGRAM),
        voice=VoiceConfig(profile_id="english_narrator"),
        enabled=enabled,
    )


def test_channel_validation():
    assert validate_channel(make_channel())==[]


def test_registry_add_get_update():
    registry=ChannelRegistry()
    channel=make_channel()
    registry.add(channel)
    assert registry.get("facts").name=="Facts"

    updated=make_channel()
    updated=ChannelConfig(
        **{**updated.__dict__,"name":"Daily Facts"}
    )
    registry.update(updated)
    assert registry.get("facts").name=="Daily Facts"


def test_duplicate_channel_rejected():
    registry=ChannelRegistry()
    registry.add(make_channel())
    with pytest.raises(ValueError):
        registry.add(make_channel())


def test_job_router_uses_channel_defaults():
    registry=ChannelRegistry()
    registry.add(make_channel())
    result=ChannelJobRouter(registry).resolve(ChannelJob(
        job_id="job1",
        channel_id="facts",
        content_source_id="source1",
        target_platforms=(Platform.YOUTUBE,),
    ))
    assert result["duration_seconds"]==300
    assert result["category"]=="facts"
    assert result["voice"].profile_id=="english_narrator"


def test_job_can_override_duration():
    registry=ChannelRegistry()
    registry.add(make_channel())
    result=ChannelJobRouter(registry).resolve(ChannelJob(
        job_id="job1",
        channel_id="facts",
        content_source_id="source1",
        target_platforms=(Platform.YOUTUBE,),
        duration_seconds=600,
    ))
    assert result["duration_seconds"]==600


def test_unsupported_platform_rejected():
    registry=ChannelRegistry()
    registry.add(make_channel())
    # Both configured platforms are valid.
    both=ChannelJobRouter(registry).resolve(ChannelJob(
        job_id="job1",
        channel_id="facts",
        content_source_id="source1",
        target_platforms=(Platform.YOUTUBE,Platform.INSTAGRAM),
    ))
    assert both["platforms"]==(Platform.YOUTUBE,Platform.INSTAGRAM)

    with pytest.raises(ValueError):
        ChannelJobRouter(registry).resolve(ChannelJob(
            job_id="job-bad",
            channel_id="facts",
            content_source_id="source1",
            target_platforms=("tiktok",),
        ))
    result=ChannelJobRouter(registry).resolve(ChannelJob(
        job_id="job2",
        channel_id="facts",
        content_source_id="source1",
        target_platforms=(Platform.INSTAGRAM,),
    ))
    assert result["platforms"]==(Platform.INSTAGRAM,)


def test_disabled_channel_rejected():
    registry=ChannelRegistry()
    registry.add(make_channel(enabled=False))
    with pytest.raises(ValueError):
        ChannelJobRouter(registry).resolve(ChannelJob(
            job_id="job1",
            channel_id="facts",
            content_source_id="source1",
            target_platforms=(Platform.YOUTUBE,),
        ))

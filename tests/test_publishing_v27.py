from pathlib import Path
import pytest

from app.services.channels.models import ChannelProfile
from app.services.channels.registry import ChannelRegistry
from app.services.channels.orchestrator import MultiChannelOrchestrator
from app.services.publishing.factory import get_publisher
from app.services.publishing.models import PublishRequest


def test_mock_publishers_are_platform_specific(tmp_path):
    video=tmp_path/"video.mp4"
    video.write_bytes(b"video")
    request=PublishRequest("kids","youtube",str(video),"Test")
    result=get_publisher("youtube",mock=True).publish(request)
    assert result.platform=="youtube"
    assert result.status=="published"


def test_youtube_requires_authentication(tmp_path):
    video=tmp_path/"video.mp4"; video.write_bytes(b"video")
    request=PublishRequest("kids","youtube",str(video),"Test")
    with pytest.raises(RuntimeError):
        get_publisher("youtube").publish(request)


def test_instagram_requires_authentication(tmp_path):
    video=tmp_path/"video.mp4"; video.write_bytes(b"video")
    request=PublishRequest("kids","instagram",str(video),"Test")
    with pytest.raises(RuntimeError):
        get_publisher("instagram").publish(request)


def test_youtube_publisher_uses_injected_service(tmp_path):
    video=tmp_path/"video.mp4"; video.write_bytes(b"video")

    class Request:
        def execute(self): return {"id":"abc123"}
    class Videos:
        def insert(self,**kwargs):
            assert kwargs["body"]["snippet"]["title"]=="Hello"
            return Request()
    class Service:
        def videos(self): return Videos()

    result=get_publisher(
        "youtube",
        service=Service(),
        media_uploader=lambda path: path,
    ).publish(
        PublishRequest("kids","youtube",str(video),"Hello")
    )
    assert result.remote_id=="abc123"
    assert result.url.endswith("abc123")

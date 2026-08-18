import pytest

from app.services.video.factory import create_video_provider
from app.services.video.mock import MockVideoProvider


def test_mock_factory():
    provider = create_video_provider("mock")
    assert isinstance(provider, MockVideoProvider)


def test_real_provider_requires_explicit_adapter():
    with pytest.raises(RuntimeError):
        create_video_provider("local")

    with pytest.raises(RuntimeError):
        create_video_provider("remote")

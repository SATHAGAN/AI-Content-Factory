import os
from datetime import date

from app.services.publishing.mock import MockPublisher
from app.services.publishing.interfaces import PublishRequest
from app.services.quota.limiter import DailyQuota, InMemoryDailyQuota


def test_mock_multi_platform_publish():
    request = PublishRequest(media_uri="/tmp/video.mp4", title="Test")
    yt = MockPublisher("youtube").publish(request)
    ig = MockPublisher("instagram").publish(request)
    assert yt.platform == "youtube"
    assert ig.platform == "instagram"
    assert yt.status == "published"


def test_dynamic_daily_quota():
    quota = InMemoryDailyQuota()
    day = date(2026, 8, 16)
    limits = DailyQuota(shorts_limit=5, long_limit=2)

    for _ in range(5):
        assert quota.consume("channel-1", "short", limits, day)
    assert not quota.consume("channel-1", "short", limits, day)

    for _ in range(2):
        assert quota.consume("channel-1", "long", limits, day)
    assert not quota.consume("channel-1", "long", limits, day)

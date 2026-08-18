from datetime import datetime

from app.services.scheduling.planner import DynamicSchedulePlanner


def test_dynamic_schedule():
    slots = DynamicSchedulePlanner().build_day(
        datetime(2026, 8, 16, 0, 0),
        shorts_target=5,
        long_target=2,
    )
    assert len(slots) == 7
    assert sum(s.content_format == "short" for s in slots) == 5
    assert sum(s.content_format == "long" for s in slots) == 2


def test_schedule_is_dynamic():
    slots = DynamicSchedulePlanner().build_day(
        datetime(2026, 8, 16, 0, 0),
        shorts_target=2,
        long_target=1,
    )
    assert len(slots) == 3

from datetime import date, datetime, timezone

from app.models.models import Channel, Organization
from app.services.scheduling.daily import DailyProductionScheduler
from app.services.scheduling.planner import DynamicSchedulePlanner


def test_planner_supports_custom_targets():
    slots = DynamicSchedulePlanner().build_day(
        datetime(2026, 8, 16, tzinfo=timezone.utc),
        3, 1, 8, 16, 18, 20
    )
    assert len(slots) == 4
    assert sum(s.content_format == "short" for s in slots) == 3
    assert sum(s.content_format == "long" for s in slots) == 1
    assert slots == sorted(slots, key=lambda x: (x.scheduled_at, x.content_format, x.sequence))


def test_daily_scheduler_is_idempotent(db_session):
    org = Organization(name="Scheduler Org")
    db_session.add(org)
    db_session.flush()
    channel = Channel(
        organization_id=org.id,
        name="Kids",
        default_language="en",
        daily_shorts_target=3,
        daily_long_target=1,
        settings={"category": "kids", "platforms": ["youtube", "instagram"]},
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)

    scheduler = DailyProductionScheduler()
    first = scheduler.plan_channel_day(db_session, channel, date(2026, 8, 17))
    second = scheduler.plan_channel_day(db_session, channel, date(2026, 8, 17))

    assert len(first) == 4
    assert len(second) == 4
    assert {x.job_id for x in first} == {x.job_id for x in second}
    assert len({x.schedule_key for x in first}) == 4

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import JobStatus
from app.models.models import Channel, GenerationJob
from app.services.scheduling.planner import DynamicSchedulePlanner, ScheduleSlot


@dataclass(frozen=True)
class ScheduledJobInfo:
    job_id: str
    schedule_key: str
    channel_id: str
    content_format: str
    scheduled_at: datetime
    status: str


class DailyProductionScheduler:
    """Persist one generation job per planned daily content slot.

    Idempotency is enforced by a unique schedule key, so the scheduler can
    safely be called repeatedly by cron, CI, or a container scheduler.
    """

    def __init__(self, planner: DynamicSchedulePlanner | None = None):
        self.planner = planner or DynamicSchedulePlanner()

    def plan_channel_day(
        self,
        db: Session,
        channel: Channel,
        day: date,
        *,
        shorts_target: int | None = None,
        long_target: int | None = None,
    ) -> list[ScheduledJobInfo]:
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        settings = channel.settings or {}
        slots = self.planner.build_day(
            start,
            channel.daily_shorts_target if shorts_target is None else shorts_target,
            channel.daily_long_target if long_target is None else long_target,
            int(settings.get("shorts_start_hour", 9)),
            int(settings.get("shorts_end_hour", 17)),
            int(settings.get("long_start_hour", 18)),
            int(settings.get("long_end_hour", 21)),
        )

        created: list[ScheduledJobInfo] = []
        for slot in slots:
            key = f"daily:{channel.id}:{day.isoformat()}:{slot.content_format}:{slot.sequence}"
            existing = db.scalar(select(GenerationJob).where(GenerationJob.schedule_key == key))
            if existing:
                created.append(ScheduledJobInfo(
                    existing.id, key, channel.id, slot.content_format, slot.scheduled_at, existing.status.value
                ))
                continue

            payload = {
                "channel_id": channel.id,
                "organization_id": channel.organization_id,
                "content_format": slot.content_format,
                "scheduled_at": slot.scheduled_at.isoformat(),
                "sequence": slot.sequence,
                "language": channel.default_language,
                "category": settings.get("category", "general"),
                "content_profile_id": settings.get("content_profile_id"),
                "platforms": settings.get("platforms", ["youtube", "instagram"]),
            }
            job = GenerationJob(
                organization_id=channel.organization_id,
                project_id=None,
                job_type="daily_content_generation",
                status=JobStatus.PENDING,
                priority=int(settings.get("generation_priority", 50)),
                schedule_key=key,
                input_data=payload,
            )
            db.add(job)
            db.flush()
            created.append(ScheduledJobInfo(
                job.id, key, channel.id, slot.content_format, slot.scheduled_at, job.status.value
            ))

        db.commit()
        return created

    def plan_organization_day(
        self, db: Session, organization_id: str, day: date
    ) -> list[ScheduledJobInfo]:
        channels = list(db.scalars(
            select(Channel).where(Channel.organization_id == organization_id).order_by(Channel.name)
        ))
        result: list[ScheduledJobInfo] = []
        for channel in channels:
            result.extend(self.plan_channel_day(db, channel, day))
        return result

from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Channel, GenerationJob, User
from app.services.scheduling.daily import DailyProductionScheduler
from app.services.scheduling.planner import DynamicSchedulePlanner

router = APIRouter(prefix="/scheduling", tags=["scheduling"])


class ScheduleRequest(BaseModel):
    start: datetime
    shorts_target: int = Field(default=5, ge=0, le=100)
    long_target: int = Field(default=2, ge=0, le=100)
    shorts_start_hour: int = Field(default=9, ge=0, le=23)
    shorts_end_hour: int = Field(default=17, ge=0, le=23)
    long_start_hour: int = Field(default=18, ge=0, le=23)
    long_end_hour: int = Field(default=21, ge=0, le=23)


class DailyRunRequest(BaseModel):
    channel_id: str | None = None
    day: date | None = None


def _slot_response(slot):
    return {
        "scheduled_at": slot.scheduled_at.isoformat(),
        "content_format": slot.content_format,
        "sequence": slot.sequence,
    }


@router.post("/preview")
def preview(payload: ScheduleRequest, current_user: User = Depends(get_current_user)):
    slots = DynamicSchedulePlanner().build_day(
        payload.start,
        payload.shorts_target,
        payload.long_target,
        payload.shorts_start_hour,
        payload.shorts_end_hour,
        payload.long_start_hour,
        payload.long_end_hour,
    )
    return {
        "organization_id": current_user.organization_id,
        "slots": [_slot_response(s) for s in slots],
    }


@router.post("/run-daily")
def run_daily(
    payload: DailyRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    day = payload.day or date.today()
    scheduler = DailyProductionScheduler()

    if payload.channel_id:
        channel = db.scalar(
            select(Channel).where(
                Channel.id == payload.channel_id,
                Channel.organization_id == current_user.organization_id,
            )
        )
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        jobs = scheduler.plan_channel_day(db, channel, day)
    else:
        jobs = scheduler.plan_organization_day(db, current_user.organization_id, day)

    return {
        "organization_id": current_user.organization_id,
        "day": day.isoformat(),
        "created_or_existing": [
            {
                "job_id": j.job_id,
                "schedule_key": j.schedule_key,
                "channel_id": j.channel_id,
                "content_format": j.content_format,
                "scheduled_at": j.scheduled_at.isoformat(),
                "status": j.status,
            }
            for j in jobs
        ],
        "count": len(jobs),
    }


@router.get("/daily-jobs")
def list_daily_jobs(
    day: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    jobs = list(db.scalars(
        select(GenerationJob)
        .where(
            GenerationJob.organization_id == current_user.organization_id,
            GenerationJob.job_type == "daily_content_generation",
        )
        .order_by(GenerationJob.schedule_key)
    ))
    result = []
    prefix = f"daily:"
    for job in jobs:
        if job.schedule_key and job.schedule_key.startswith(prefix) and job.input_data.get("scheduled_at", "").startswith(day.isoformat()):
            result.append({
                "id": job.id,
                "schedule_key": job.schedule_key,
                "channel_id": job.input_data.get("channel_id"),
                "content_format": job.input_data.get("content_format"),
                "scheduled_at": job.input_data.get("scheduled_at"),
                "status": job.status.value,
            })
    return result

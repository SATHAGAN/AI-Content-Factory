from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.models import User
from app.services.jobs.manager import JobManager
from app.services.jobs.queue import InMemoryJobQueue

router = APIRouter(prefix="/jobs", tags=["jobs"])

_queue = InMemoryJobQueue()
_manager = JobManager(_queue)


class JobCreate(BaseModel):
    job_type: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)
    priority: int = Field(default=100, ge=1, le=1000)


def _response(job):
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status.value,
        "priority": job.priority,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
        "error": job.error,
    }


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def submit_job(payload: JobCreate, current_user: User = Depends(get_current_user)):
    job = _manager.submit(
        payload.job_type,
        {"organization_id": current_user.organization_id, **payload.payload},
        priority=payload.priority,
    )
    return _response(job)


@router.get("")
def list_jobs(current_user: User = Depends(get_current_user)):
    jobs = [
        job for job in _queue.list()
        if job.payload.get("organization_id") == current_user.organization_id
    ]
    return [_response(job) for job in jobs]


@router.get("/{job_id}")
def get_job(job_id: str, current_user: User = Depends(get_current_user)):
    job = _queue.get(job_id)
    if not job or job.payload.get("organization_id") != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return _response(job)

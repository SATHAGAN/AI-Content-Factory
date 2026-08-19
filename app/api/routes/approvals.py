from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import JobStatus
from app.models.models import GenerationJob, Project, User

router = APIRouter(prefix="/workspace/jobs", tags=["workspace-approval"])


def _transition(job: GenerationJob, project: Project, *, status: str, message: str, db) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    output = dict(job.output_data or {})
    output.update({
        "status": status,
        "stage": "approval",
        "progress": 100,
        "message": message,
        "updated_at": now,
    })
    job.output_data = output
    job.status = JobStatus.SUCCEEDED if status == "approved" else JobStatus.CANCELLED

    project_settings = dict(project.settings or {})
    project_settings["_updated_at"] = now
    project.status = "approved" if status == "approved" else "rejected"
    project.settings = project_settings

    db.commit()
    db.refresh(job)
    return output


@router.post("/{job_id}/approve")
def approve_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    job = (
        db.query(GenerationJob)
        .filter(
            GenerationJob.id == job_id,
            GenerationJob.organization_id == user.organization_id,
        )
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if (job.output_data or {}).get("status") != "awaiting_approval":
        raise HTTPException(status_code=409, detail="Job is not awaiting approval")

    project = db.query(Project).filter(
        Project.id == job.project_id,
        Project.organization_id == user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    output = _transition(
        job, project,
        status="approved",
        message="Generation approved",
        db=db,
    )
    return {"job_id": job.id, "status": output["status"], "message": output["message"]}


@router.post("/{job_id}/reject")
def reject_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    job = (
        db.query(GenerationJob)
        .filter(
            GenerationJob.id == job_id,
            GenerationJob.organization_id == user.organization_id,
        )
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if (job.output_data or {}).get("status") != "awaiting_approval":
        raise HTTPException(status_code=409, detail="Job is not awaiting approval")

    project = db.query(Project).filter(
        Project.id == job.project_id,
        Project.organization_id == user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    output = _transition(
        job, project,
        status="rejected",
        message="Generation rejected",
        db=db,
    )
    return {"job_id": job.id, "status": output["status"], "message": output["message"]}

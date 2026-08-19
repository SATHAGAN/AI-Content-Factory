from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

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


def _get_job(job_id: str, user: User, db):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id,
        GenerationJob.organization_id == user.organization_id,
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def _get_project(job: GenerationJob, user: User, db):
    project = db.query(Project).filter(
        Project.id == job.project_id,
        Project.organization_id == user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _approval_ready(job: GenerationJob) -> bool:
    output = job.output_data or {}
    return output.get("stage") == "approval" and bool(output.get("final_video_path"))


@router.get("/{job_id}/artifact")
def get_artifact(job_id: str, user: User = Depends(get_current_user), db=Depends(get_db)):
    job = _get_job(job_id, user, db)
    path = Path((job.output_data or {}).get("final_video_path", "")).resolve()
    root = Path(os.getenv("ARTIFACT_ROOT", "artifacts/jobs")).resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Generated video artifact is not available")
    return FileResponse(path, media_type="video/mp4", filename=f"{job_id}.mp4")


@router.post("/{job_id}/approve")
def approve_job(job_id: str, user: User = Depends(get_current_user), db=Depends(get_db)):
    job = _get_job(job_id, user, db)
    if not _approval_ready(job):
        raise HTTPException(status_code=409, detail="Job is not awaiting approval or has no video artifact")
    project = _get_project(job, user, db)
    output = _transition(job, project, status="approved", message="Generation approved", db=db)
    return {"job_id": job.id, "status": output["status"], "message": output["message"]}


@router.post("/{job_id}/reject")
def reject_job(job_id: str, user: User = Depends(get_current_user), db=Depends(get_db)):
    job = _get_job(job_id, user, db)
    if not _approval_ready(job):
        raise HTTPException(status_code=409, detail="Job is not awaiting approval or has no video artifact")
    project = _get_project(job, user, db)
    output = _transition(job, project, status="rejected", message="Generation rejected", db=db)
    return {"job_id": job.id, "status": output["status"], "message": output["message"]}

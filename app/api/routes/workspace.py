from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import JobStatus
from app.models.models import GenerationJob, Project, User
from app.services.pipeline.real_worker import real_generation_worker
from app.services.pipeline.worker import generation_worker


router = APIRouter(prefix="/workspace", tags=["workspace"])
PIPELINE_MODE = os.getenv("PIPELINE_MODE", "production").lower()


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = "General"
    language: str = "English"
    format: str = "short"
    duration_seconds: int = Field(default=60, ge=15, le=3600)
    source_text: str = Field(min_length=1, max_length=100000)
    channel_ids: list[str] = Field(default_factory=list)
    video_model: str = "Wan2.1 T2V 1.3B"
    tts_model: str = "Qwen3-TTS 0.6B"
    judge_model: str = "Local Multimodal Judge"
    approval_required: bool = True
    auto_publish: bool = False


class GenerateRequest(BaseModel):
    project_id: str


class ApprovalRequest(BaseModel):
    approved: bool
    comment: str | None = Field(default=None, max_length=2000)


def _project_response(project: Project) -> dict:
    settings = project.settings or {}
    return {
        "id": project.id,
        "organization_id": project.organization_id,
        "name": project.name,
        "category": settings.get("category", "General"),
        "language": settings.get("language", "English"),
        "format": settings.get("format", "short"),
        "duration_seconds": settings.get("duration_seconds", 60),
        "source_text": settings.get("source_text", ""),
        "channel_ids": settings.get("channel_ids", []),
        "video_model": settings.get("video_model", "Wan2.1 T2V 1.3B"),
        "tts_model": settings.get("tts_model", "Qwen3-TTS 0.6B"),
        "judge_model": settings.get("judge_model", "Local Multimodal Judge"),
        "approval_required": settings.get("approval_required", True),
        "auto_publish": settings.get("auto_publish", False),
        "status": project.status,
        "created_at": settings.get("_created_at"),
        "updated_at": settings.get("_updated_at"),
    }


def _job_response(job: GenerationJob) -> dict:
    output_data = job.output_data or {}
    return {
        "id": job.id,
        "project_id": job.project_id,
        "organization_id": job.organization_id,
        "type": job.job_type,
        "status": output_data.get("status", job.status.value),
        "stage": output_data.get("stage", "queued"),
        "progress": output_data.get("progress", 0),
        "message": output_data.get("message", "Generation request accepted"),
        "created_at": output_data.get("created_at"),
        "updated_at": output_data.get("updated_at"),
        "final_video_path": output_data.get("final_video_path"),
        "video_url": f"/api/v1/workspace/jobs/{job.id}/video" if output_data.get("final_video_path") else None,
        "model_id": output_data.get("model_id"),
        "scene_count": output_data.get("scene_count"),
        "duration_seconds": output_data.get("duration_seconds"),
        "approval_comment": output_data.get("approval_comment"),
    }


def _get_project(db: Session, user: User, project_id: str) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.organization_id == user.organization_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects", status_code=201)
def create_project(payload: ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    project = Project(
        id=str(uuid4()),
        organization_id=user.organization_id,
        name=payload.name,
        status="draft",
        settings={
            "category": payload.category,
            "language": payload.language,
            "format": payload.format,
            "duration_seconds": payload.duration_seconds,
            "source_text": payload.source_text,
            "channel_ids": payload.channel_ids,
            "video_model": payload.video_model,
            "tts_model": payload.tts_model,
            "judge_model": payload.judge_model,
            "approval_required": payload.approval_required,
            "auto_publish": payload.auto_publish,
            "_created_at": now,
            "_updated_at": now,
        },
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_response(project)


@router.get("/projects")
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = (
        db.query(Project)
        .filter(Project.organization_id == user.organization_id)
        .order_by(Project.name.asc())
        .all()
    )
    return [_project_response(project) for project in projects]


@router.get("/projects/{project_id}")
def get_project(project_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _project_response(_get_project(db, user, project_id))


@router.post("/generate", status_code=202)
def enqueue_generation(
    payload: GenerateRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project(db, user, payload.project_id)
    now = datetime.now(timezone.utc).isoformat()
    job = GenerationJob(
        id=str(uuid4()),
        organization_id=user.organization_id,
        project_id=project.id,
        job_type="content_generation",
        status=JobStatus.QUEUED,
        input_data={"project_id": project.id, "source_text": (project.settings or {}).get("source_text", "")},
        output_data={
            "status": "queued", "stage": "queued", "progress": 0,
            "message": "Generation request accepted", "created_at": now, "updated_at": now,
        },
    )
    project.status = "queued"
    settings = dict(project.settings or {})
    settings["_updated_at"] = now
    project.settings = settings
    db.add(job)
    db.commit()
    db.refresh(job)

    if PIPELINE_MODE == "development":
        background_tasks.add_task(generation_worker.run, job.id)
    else:
        background_tasks.add_task(real_generation_worker.run, job.id)
    return _job_response(job)


@router.get("/jobs")
def list_jobs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    jobs = (
        db.query(GenerationJob)
        .filter(GenerationJob.organization_id == user.organization_id)
        .order_by(GenerationJob.id.desc())
        .all()
    )
    return [_job_response(job) for job in jobs]


@router.get("/jobs/{job_id}")
def get_job(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id, GenerationJob.organization_id == user.organization_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_response(job)


@router.get("/jobs/{job_id}/video")
def get_job_video(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id, GenerationJob.organization_id == user.organization_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    path = (job.output_data or {}).get("final_video_path")
    if not path:
        raise HTTPException(status_code=404, detail="Video is not ready")
    file_path = Path(path).resolve()
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Video artifact is no longer available")
    return FileResponse(file_path, media_type="video/mp4", filename=f"{job.id}.mp4")


@router.post("/jobs/{job_id}/approval")
def approve_job(
    job_id: str,
    payload: ApprovalRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id, GenerationJob.organization_id == user.organization_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    output = dict(job.output_data or {})
    if output.get("stage") != "approval":
        raise HTTPException(status_code=409, detail="Job is not awaiting approval")
    if not output.get("final_video_path"):
        raise HTTPException(status_code=409, detail="No generated video is available for approval")

    now = datetime.now(timezone.utc).isoformat()
    output["approval_comment"] = payload.comment
    output["approved_at"] = now
    output["updated_at"] = now
    output["status"] = "approved" if payload.approved else "rejected"
    output["message"] = "Video approved for publishing" if payload.approved else "Video rejected"
    job.output_data = output

    project = db.query(Project).filter(Project.id == job.project_id).first()
    if project:
        project.status = "approved" if payload.approved else "rejected"
        settings = dict(project.settings or {})
        settings["_updated_at"] = now
        project.settings = settings

    db.commit()
    db.refresh(job)
    return _job_response(job)

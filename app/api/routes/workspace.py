from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.models import User
from app.services.pipeline.worker import generation_worker
from app.services.workers.registry import job_registry

router = APIRouter(prefix="/workspace", tags=["workspace"])

PROJECTS: dict[str, dict] = {}


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


@router.post("/projects", status_code=201)
def create_project(payload: ProjectCreate, user: User = Depends(get_current_user)):
    project_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    PROJECTS[project_id] = {
        "id": project_id,
        "organization_id": user.organization_id,
        **payload.model_dump(),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    return PROJECTS[project_id]


@router.get("/projects")
def list_projects(user: User = Depends(get_current_user)):
    return [p for p in PROJECTS.values() if p["organization_id"] == user.organization_id]


@router.get("/projects/{project_id}")
def get_project(project_id: str, user: User = Depends(get_current_user)):
    project = PROJECTS.get(project_id)
    if not project or project["organization_id"] != user.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


class GenerateRequest(BaseModel):
    project_id: str


@router.post("/generate", status_code=202)
def enqueue_generation(
    payload: GenerateRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    project = PROJECTS.get(payload.project_id)
    if not project or project["organization_id"] != user.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")

    job_id = str(uuid4())
    job = {
        "id": job_id,
        "project_id": project["id"],
        "organization_id": user.organization_id,
        "type": "content_generation",
        "status": "queued",
        "stage": "queued",
        "progress": 0,
        "message": "Generation request accepted",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    job_registry.put(job_id, job)
    project["status"] = "queued"
    project["updated_at"] = datetime.now(timezone.utc).isoformat()

    background_tasks.add_task(generation_worker.run, job_id)
    return job


@router.get("/jobs")
def list_jobs(user: User = Depends(get_current_user)):
    return job_registry.all(user.organization_id)


@router.get("/jobs/{job_id}")
def get_job(job_id: str, user: User = Depends(get_current_user)):
    job = job_registry.get(job_id)
    if not job or job["organization_id"] != user.organization_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

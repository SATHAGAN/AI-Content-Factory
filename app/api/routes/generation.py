from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.models import User
from app.services.jobs.manager import JobManager
from app.services.jobs.queue import InMemoryJobQueue

router = APIRouter(prefix="/generation", tags=["generation"])
_queue = InMemoryJobQueue()
_manager = JobManager(_queue)


class SceneGenerationRequest(BaseModel):
    scene: dict
    language: str = "en"
    voice: str = "default"
    voice_speed: float = Field(default=1.0, gt=0.1, le=3.0)
    width: int = Field(default=480, ge=256, le=1920)
    height: int = Field(default=832, ge=256, le=1920)
    frames: int = Field(default=97, ge=8, le=5000)
    fps: int = Field(default=16, ge=1, le=60)
    seed: int | None = None


@router.post("/scene", status_code=status.HTTP_202_ACCEPTED)
def enqueue_scene(
    payload: SceneGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    job = _manager.submit(
        "generate_scene",
        {"organization_id": current_user.organization_id, **payload.model_dump()},
        priority=20,
    )
    return {
        "job_id": job.id,
        "status": job.status.value,
        "job_type": job.job_type,
    }

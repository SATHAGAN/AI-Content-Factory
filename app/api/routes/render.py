from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.models import User
from app.services.render.pipeline import ProductionRenderPipeline

router = APIRouter(prefix="/render", tags=["render"])


class RenderRequest(BaseModel):
    scene_paths: list[str] = Field(min_length=1)
    output_path: str = "./data/render/final.mp4"
    audio_path: str | None = None


@router.post("")
def render(
    payload: RenderRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = ProductionRenderPipeline().render(
            payload.scene_paths,
            payload.output_path,
            payload.audio_path,
        )
        return {
            "organization_id": current_user.organization_id,
            "video_path": result.video_path,
            "qa": result.qa,
        }
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

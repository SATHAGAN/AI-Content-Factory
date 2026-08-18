from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.models import User
from app.services.qa.advanced_video_qa import AdvancedVideoQA

router = APIRouter(prefix="/qa", tags=["qa"])


class QARequest(BaseModel):
    video_path: str
    require_audio: bool = True


@router.post("/video")
def check_video(payload: QARequest, current_user: User = Depends(get_current_user)):
    result = AdvancedVideoQA().check(payload.video_path, payload.require_audio)
    return {
        "organization_id": current_user.organization_id,
        **result.to_dict(),
    }

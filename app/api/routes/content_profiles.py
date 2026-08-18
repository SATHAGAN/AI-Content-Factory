from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import ContentProfile, User
from app.schemas.common import ContentProfileCreate, ContentProfileResponse

router = APIRouter(prefix="/content-profiles", tags=["content-profiles"])


@router.post("", response_model=ContentProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: ContentProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = ContentProfile(
        organization_id=current_user.organization_id,
        **payload.model_dump(),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=list[ContentProfileResponse])
def list_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(ContentProfile)
            .where(ContentProfile.organization_id == current_user.organization_id)
            .order_by(ContentProfile.name)
        )
    )

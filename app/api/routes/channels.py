from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Channel, User
from app.schemas.common import ChannelCreate, ChannelResponse

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
def create_channel(
    payload: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    channel = Channel(
        organization_id=current_user.organization_id,
        **payload.model_dump(),
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


@router.get("", response_model=list[ChannelResponse])
def list_channels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Channel)
            .where(Channel.organization_id == current_user.organization_id)
            .order_by(Channel.name)
        )
    )

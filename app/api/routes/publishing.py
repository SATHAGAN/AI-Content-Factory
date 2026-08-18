from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.models import User
from app.services.publishing.interfaces import PublishRequest
from app.services.publishing.service import MultiChannelPublisher
from app.services.quota.limiter import DailyQuota, InMemoryDailyQuota
from datetime import date

router = APIRouter(prefix="/publishing", tags=["publishing"])
quota = InMemoryDailyQuota()


class PublishTarget(BaseModel):
    platform: str
    media_uri: str
    content_format: str = "short"
    title: str | None = None
    description: str | None = None
    caption: str | None = None
    tags: list[str] = Field(default_factory=list)
    privacy: str = "private"
    metadata: dict = Field(default_factory=dict)


class PublishRequestBody(BaseModel):
    channel_id: str
    shorts_limit: int = Field(default=5, ge=0, le=100)
    long_limit: int = Field(default=2, ge=0, le=100)
    targets: list[PublishTarget] = Field(min_length=1)


@router.post("/publish", status_code=status.HTTP_202_ACCEPTED)
def publish(
    payload: PublishRequestBody,
    current_user: User = Depends(get_current_user),
):
    day = date.today()
    dq = DailyQuota(payload.shorts_limit, payload.long_limit)
    reserved: list[tuple[str, PublishTarget]] = []

    for target in payload.targets:
        if target.content_format not in {"short", "long"}:
            raise HTTPException(status_code=422, detail="content_format must be short or long")
        if not quota.consume(payload.channel_id, target.content_format, dq, day):
            raise HTTPException(
                status_code=429,
                detail=f"Daily {target.content_format} quota reached for this channel"
            )
        reserved.append((target.platform, target))

    targets = [
        (
            platform,
            PublishRequest(
                media_uri=target.media_uri,
                title=target.title,
                description=target.description,
                caption=target.caption,
                tags=target.tags,
                privacy=target.privacy,
                metadata=target.metadata,
            ),
        )
        for platform, target in reserved
    ]

    result = MultiChannelPublisher().publish(targets)
    return {
        "organization_id": current_user.organization_id,
        "published": [r.__dict__ for r in result.results],
        "errors": result.errors,
    }

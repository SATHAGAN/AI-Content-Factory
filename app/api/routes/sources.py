from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import SourceType
from app.models.models import SourceDocument, User
from app.schemas.common import SourceCreate

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_source(
    payload: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        source_type = SourceType(payload.source_type)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unsupported source_type: {payload.source_type}")

    source = SourceDocument(
        organization_id=current_user.organization_id,
        source_type=source_type,
        title=payload.title,
        content_text=payload.content_text,
        storage_uri=payload.storage_uri,
        metadata=payload.metadata,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return {"id": source.id, "source_type": source.source_type.value}

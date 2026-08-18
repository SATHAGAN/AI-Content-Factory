from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Channel, ContentProfile, Project, SourceDocument, User
from app.schemas.common import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


def _owned(db: Session, model, object_id: str | None, organization_id: str):
    if not object_id:
        return None
    obj = db.get(model, object_id)
    if not obj or getattr(obj, "organization_id", None) != organization_id:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org_id = current_user.organization_id
    _owned(db, Channel, payload.channel_id, org_id)
    _owned(db, ContentProfile, payload.content_profile_id, org_id)
    _owned(db, SourceDocument, payload.source_document_id, org_id)

    project = Project(
        organization_id=org_id,
        name=payload.name,
        channel_id=payload.channel_id,
        content_profile_id=payload.content_profile_id,
        source_document_id=payload.source_document_id,
        settings=payload.settings,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Project)
            .where(Project.organization_id == current_user.organization_id)
            .order_by(Project.name)
        )
    )

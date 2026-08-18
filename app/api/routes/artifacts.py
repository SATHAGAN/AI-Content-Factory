from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.api.deps import get_current_user
from app.models.models import User
from app.services.artifacts.store import ArtifactStore

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.post("/upload")
async def upload_artifact(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    safe_name = file.filename.replace("\\", "/").split("/")[-1]
    key = f"organizations/{current_user.organization_id}/uploads/{safe_name}"
    data = await file.read()

    uri = ArtifactStore().put_bytes(key, data, file.content_type)
    return {"key": key, "uri": uri, "size_bytes": len(data)}

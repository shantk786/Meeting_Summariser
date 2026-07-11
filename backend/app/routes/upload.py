from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import UploadResponse
from app.services.storage_service import StorageService
from app.main_deps import get_storage_service

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
) -> UploadResponse:
    try:
        file_path, _ = storage_service.save_upload(file)
        meeting = crud.create_meeting(db, file.filename or "meeting-audio", file_path)
        return UploadResponse(
            meeting={
                "id": meeting.id,
                "filename": meeting.filename,
                "status": meeting.status,
                "created_at": meeting.created_at,
            },
            message="Audio uploaded successfully. You can now process the meeting.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {exc}") from exc

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import MeetingStatus
from app.schemas import MeetingDetail, MeetingListResponse, ProcessResponse
from app.services.pipeline_service import PipelineService
from app.main_deps import get_pipeline_service

router = APIRouter(tags=["meeting"])


@router.get("/meeting/{meeting_id}", response_model=MeetingDetail)
def get_meeting(meeting_id: str, db: Session = Depends(get_db)) -> MeetingDetail:
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")
    return MeetingDetail(
        id=meeting.id,
        filename=meeting.filename,
        status=MeetingStatus(meeting.status),
        transcript=meeting.transcript,
        summary=meeting.summary,
        key_points=meeting.key_points or [],
        decisions=meeting.decisions or [],
        action_items=meeting.action_items or [],
        error_message=meeting.error_message,
        created_at=meeting.created_at,
        file_url=f"/uploads/{Path(meeting.file_path).name}",
        processed=meeting.status == MeetingStatus.completed.value,
    )


@router.post("/process/{meeting_id}", response_model=ProcessResponse)
def process_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
) -> ProcessResponse:
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    processed = pipeline_service.process(db, meeting)
    return ProcessResponse(
        meeting=MeetingDetail(
            id=processed.id,
            filename=processed.filename,
            status=MeetingStatus(processed.status),
            transcript=processed.transcript,
            summary=processed.summary,
            key_points=processed.key_points or [],
            decisions=processed.decisions or [],
            action_items=processed.action_items or [],
            error_message=processed.error_message,
            created_at=processed.created_at,
            file_url=f"/uploads/{Path(processed.file_path).name}",
            processed=processed.status == MeetingStatus.completed.value,
        ),
        message="Meeting processed successfully.",
    )


@router.get("/meetings", response_model=MeetingListResponse)
def list_meetings(
    query: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
) -> MeetingListResponse:
    meetings = crud.list_meetings(db, query=query)
    items = [
        {
            "id": meeting.id,
            "filename": meeting.filename,
            "status": meeting.status,
            "transcript": meeting.transcript,
            "summary": meeting.summary,
            "key_points": meeting.key_points or [],
            "decisions": meeting.decisions or [],
            "action_items": meeting.action_items or [],
            "error_message": meeting.error_message,
            "created_at": meeting.created_at,
        }
        for meeting in meetings
    ]
    return MeetingListResponse(items=items, total=len(items))


@router.delete("/meeting/{meeting_id}")
def delete_meeting(meeting_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")
    file_path = meeting.file_path
    crud.delete_meeting(db, meeting)
    Path(file_path).unlink(missing_ok=True)
    return {"message": "Meeting deleted successfully."}

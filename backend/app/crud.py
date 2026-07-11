from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Meeting, MeetingStatus


def create_meeting(db: Session, filename: str, file_path: str) -> Meeting:
    meeting = Meeting(filename=filename, file_path=file_path, status=MeetingStatus.uploaded.value)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def get_meeting(db: Session, meeting_id: str) -> Meeting | None:
    return db.get(Meeting, meeting_id)


def list_meetings(db: Session, query: str | None = None, processed_only: bool = True) -> Sequence[Meeting]:
    statement = select(Meeting).order_by(Meeting.created_at.desc())
    if processed_only:
        statement = statement.where(Meeting.status != MeetingStatus.uploaded.value)
    if query:
        like_pattern = f"%{query}%"
        statement = statement.where(Meeting.filename.ilike(like_pattern))
    return db.scalars(statement).all()


def update_meeting(db: Session, meeting: Meeting) -> Meeting:
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def delete_meeting(db: Session, meeting: Meeting) -> None:
    db.delete(meeting)
    db.commit()

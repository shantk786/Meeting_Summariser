from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models import MeetingStatus


class ActionItem(BaseModel):
    task: str
    owner: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[str] = None


class MeetingAnalysis(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)


class MeetingBase(BaseModel):
    filename: str
    status: MeetingStatus


class MeetingCreateResponse(MeetingBase):
    id: str
    created_at: datetime


class MeetingListItem(MeetingBase):
    id: str
    transcript: Optional[str] = None
    summary: Optional[str] = None
    key_points: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    error_message: Optional[str] = None
    created_at: datetime


class MeetingDetail(MeetingListItem):
    file_url: str
    processed: bool
    transcript: Optional[str] = None


class UploadResponse(BaseModel):
    meeting: MeetingCreateResponse
    message: str


class ProcessResponse(BaseModel):
    meeting: MeetingDetail
    message: str


class MeetingListResponse(BaseModel):
    items: list[MeetingListItem]
    total: int


class ErrorResponse(BaseModel):
    detail: str

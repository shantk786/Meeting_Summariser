from __future__ import annotations

from fastapi import HTTPException, status

from app.crud import update_meeting
from app.models import Meeting, MeetingStatus
from app.schemas import MeetingAnalysis
from app.services.llm_service import LLMService
from app.services.speech_service import SpeechService


class PipelineService:
    def __init__(self, speech_service: SpeechService, llm_service: LLMService) -> None:
        self.speech_service = speech_service
        self.llm_service = llm_service

    def process(self, db, meeting: Meeting) -> Meeting:
        meeting.status = MeetingStatus.processing.value
        meeting.error_message = None
        update_meeting(db, meeting)

        try:
            transcript = self.speech_service.transcribe(meeting.file_path)
            analysis: MeetingAnalysis = self.llm_service.summarize(transcript)

            meeting.transcript = transcript
            meeting.summary = analysis.summary
            meeting.key_points = analysis.key_points
            meeting.decisions = analysis.decisions
            meeting.action_items = [item.model_dump() for item in analysis.action_items]
            meeting.status = MeetingStatus.completed.value
            meeting.error_message = None
            return update_meeting(db, meeting)
        except Exception as exc:
            meeting.status = MeetingStatus.failed.value
            meeting.error_message = str(exc)
            update_meeting(db, meeting)
            if isinstance(exc, HTTPException):
                raise
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

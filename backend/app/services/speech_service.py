from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from fastapi import HTTPException, status

from app.config import Settings

logger = logging.getLogger(__name__)


class TranscriptionProvider(Protocol):
    def transcribe(self, audio_path: str) -> str:
        ...


class OpenAIWhisperProvider:
    def __init__(self, api_key: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return response.text.strip()


class LocalWhisperProvider:
    def __init__(self, model_size: str) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover - dependency issue
            raise RuntimeError(
                "Local transcription requires the 'faster-whisper' package. Install backend dependencies first."
            ) from exc

        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str) -> str:
        segments, _info = self.model.transcribe(audio_path, beam_size=5, vad_filter=True)
        transcript = " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()
        return transcript


class SpeechService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider = self._build_provider()

    def _build_provider(self) -> TranscriptionProvider:
        provider = self.settings.transcription_provider.lower().strip()
        if provider == "openai":
            if not self.settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is required when TRANSCRIPTION_PROVIDER=openai.")
            return OpenAIWhisperProvider(self.settings.openai_api_key)
        return LocalWhisperProvider(self.settings.whisper_model)

    def transcribe(self, audio_path: str) -> str:
        try:
            transcript = self.provider.transcribe(audio_path)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Transcription failed for %s", audio_path)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Speech recognition failed: {exc}",
            ) from exc

        if not transcript:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No speech was detected in the audio file.")
        return transcript

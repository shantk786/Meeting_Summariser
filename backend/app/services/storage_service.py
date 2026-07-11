from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import Settings

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".webm", ".mp4"}


class StorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.upload_dir = settings.upload_path
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_audio_file(self, file: UploadFile) -> None:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Please upload mp3, wav, m4a, aac, flac, ogg, webm, or mp4.",
            )

    def save_upload(self, file: UploadFile) -> tuple[str, int]:
        self.validate_audio_file(file)

        safe_name = Path(file.filename or "meeting-audio").name
        unique_name = f"{uuid4().hex}_{safe_name}"
        destination = self.upload_dir / unique_name
        max_bytes = self.settings.max_upload_mb * 1024 * 1024
        total_bytes = 0

        try:
            with destination.open("wb") as buffer:
                while True:
                    chunk = file.file.read(1024 * 1024)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > max_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large. Maximum allowed size is {self.settings.max_upload_mb} MB.",
                        )
                    buffer.write(chunk)
        finally:
            file.file.close()

        if total_bytes == 0:
            destination.unlink(missing_ok=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        return str(destination), total_bytes

    def delete_file(self, file_path: str) -> None:
        path = Path(file_path)
        if path.exists():
            path.unlink()

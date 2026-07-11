from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Meeting Summarizer"
    app_env: str = "development"
    database_url: str = "sqlite:///./meeting_summarizer.db"
    upload_dir: str = "./app/uploads"
    max_upload_mb: int = 100
    cors_origins: str = "http://localhost:5173"
    transcription_provider: str = "local"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    whisper_model: str = "small"

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir).resolve()

    @property
    def allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    return settings

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, engine
from app.routes.meeting import router as meeting_router
from app.routes.upload import router as upload_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered meeting summarizer with speech-to-text, Gemini analysis, and structured meeting storage.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(settings.upload_path)), name="uploads")
app.include_router(upload_router)
app.include_router(meeting_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Meeting Summarizer API is running."}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

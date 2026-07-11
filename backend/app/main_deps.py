from functools import lru_cache

from app.config import get_settings
from app.services.llm_service import LLMService
from app.services.pipeline_service import PipelineService
from app.services.storage_service import StorageService
from app.services.speech_service import SpeechService


@lru_cache
def get_storage_service() -> StorageService:
    return StorageService(get_settings())


@lru_cache
def get_speech_service() -> SpeechService:
    return SpeechService(get_settings())


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService(get_settings())


@lru_cache
def get_pipeline_service() -> PipelineService:
    return PipelineService(get_speech_service(), get_llm_service())

from __future__ import annotations

import json
import logging
import re
from typing import Any

from fastapi import HTTPException, status

from app.config import Settings
from app.schemas import MeetingAnalysis

logger = logging.getLogger(__name__)


class GeminiProvider:
    def __init__(self, api_key: str, model_name: str) -> None:
        self.api_key = api_key
        self.model_name = model_name

        try:
            from google import genai
        except ImportError:
            genai = None

        self._genai = genai

        if self._genai is None:
            raise RuntimeError("The google-genai package is required for Gemini integration.")

        self.client = self._genai.Client(api_key=api_key)

    def generate(self, transcript: str) -> str:
        prompt = self._build_prompt(transcript)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )
        text = getattr(response, "text", None)
        if not text:
            text = str(response)
        return text

    def _build_prompt(self, transcript: str) -> str:
        return f"""
You are an expert meeting analyst.

Return only valid JSON matching this schema:
{{
  "summary": "string",
  "key_points": ["string"],
  "decisions": ["string"],
  "action_items": [
    {{
      "task": "string",
      "owner": "string or null",
      "deadline": "string or null",
      "priority": "Low | Medium | High | null"
    }}
  ]
}}

Rules:
- Do not hallucinate facts.
- If a field is missing, use null for values or an empty array when appropriate.
- Keep the summary concise and executive-friendly.
- Include only concrete decisions and action items that are supported by the transcript.
- Preserve business meaning and avoid repetition.

Transcript:
{transcript}
""".strip()


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required for summary generation.")
        self.provider = GeminiProvider(self.settings.gemini_api_key, self.settings.gemini_model)

    def summarize(self, transcript: str) -> MeetingAnalysis:
        try:
            raw_output = self.provider.generate(transcript)
            payload = self._extract_json(raw_output)
            return MeetingAnalysis.model_validate(payload)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("LLM summarization failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM timeout or parsing failure: {exc}",
            ) from exc

    def _extract_json(self, raw_output: str) -> Any:
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned.strip(), flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

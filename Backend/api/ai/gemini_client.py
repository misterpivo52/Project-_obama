import os
from typing import Optional
import requests
from django.conf import settings


class GeminiError(Exception):


def _build_url(model: str) -> str:
    base = getattr(settings, "GEMINI_BASE_URL", "").strip() or "https://generativelanguage.googleapis.com/v1beta"
    return f"{base}/models/{model}:generateContent"


def call_gemini(prompt: str, model: Optional[str] = None, timeout: Optional[int] = None) -> str:
    api_key = getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not configured")

    model_name = model or getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
    req_timeout = timeout or getattr(settings, "GEMINI_TIMEOUT", 10)

    url = f"{_build_url(model_name)}?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}],
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, timeout=req_timeout)
    except requests.RequestException as exc:
        raise GeminiError(f"Network error: {exc}") from exc

    if resp.status_code >= 400:
        raise GeminiError(f"Gemini HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise GeminiError("Gemini returned no candidates")

    content = candidates[0].get("content", {})
    parts = content.get("parts") or []
    for part in parts:
        text = part.get("text")
        if text:
            return text

    raise GeminiError("Gemini response missing text")


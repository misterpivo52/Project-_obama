import os
from typing import Optional
import requests
from django.conf import settings


class OpenAIError(Exception):


def _build_url() -> str:
    base = getattr(settings, "OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1"
    return f"{base.rstrip('/')}/chat/completions"


def call_openai(prompt: str, model: Optional[str] = None, timeout: Optional[int] = None) -> str:
    api_key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIError("OPENAI_API_KEY is not configured")

    model_name = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
    req_timeout = timeout or getattr(settings, "OPENAI_TIMEOUT", 10)

    url = _build_url()
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=req_timeout)
    except requests.RequestException as exc:
        raise OpenAIError(f"Network error: {exc}") from exc

    if resp.status_code >= 400:
        raise OpenAIError(f"OpenAI HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise OpenAIError("OpenAI returned no choices")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if content:
        return content

    raise OpenAIError("OpenAI response missing content")

# women_safety_ai

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

import requests


FALLBACK_MESSAGE = (
    "I’m sorry, I’m unable to respond right now. Let’s revisit this topic in a moment."
)

_ENV_LOADED = False
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


def _load_env_file(path: Optional[str] = None) -> None:
    """Populate os.environ using a simple KEY=VALUE .env file."""
    default_path = Path(__file__).resolve().parent.parent / "environment" / ".env"
    env_path = Path(path) if path else default_path
    if not env_path.exists():
        return

    try:
        with env_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key and value and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        # File access issues should not block manual env configuration.
        pass


def ensure_env_loaded(path: Optional[str] = None) -> None:
    """One-time load of environment variables from environment/.env."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _load_env_file(path)
    _ENV_LOADED = True


def _require_api_key() -> str:
    ensure_env_loaded()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    return api_key


def chat(
    messages: List[Dict[str, str]],
    model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.8,
    presence_penalty: float = 0.4,
) -> str:
    """
    messages: [{"role":"system"/"user"/"assistant","content":"..."}]
    Return assistant text content only.
    Include minimal error handling and fallback message if exception occurs.
    """

    try:
        api_key = _require_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        http_referer = os.getenv("OPENROUTER_SITE_URL")
        if http_referer:
            headers["HTTP-Referer"] = http_referer

        app_name = os.getenv("OPENROUTER_APP_NAME")
        if app_name:
            headers["X-Title"] = app_name

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "presence_penalty": presence_penalty,
        }

        response = requests.post(
            OPENROUTER_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices") or []
        if not choices:
            return FALLBACK_MESSAGE
        first_choice = choices[0] or {}
        message = first_choice.get("message") or {}
        content = message.get("content")
        if not content:
            return FALLBACK_MESSAGE
        return content.strip()
    except Exception:
        return FALLBACK_MESSAGE


def format_chat_payload(system_prompt: str, history: List[Dict[str, str]], user_text: str) -> List[Dict[str, str]]:
    """
    Compose messages in order: system, history..., user
    history is a list of dicts with role/user/assistant and content.
    """

    payload: List[Dict[str, str]] = []
    if system_prompt:
        payload.append({"role": "system", "content": system_prompt})

    for turn in history or []:
        role = turn.get("role")
        content = turn.get("content")
        if not role or not content:
            continue
        payload.append({"role": role, "content": content})

    if user_text:
        payload.append({"role": "user", "content": user_text})

    return payload

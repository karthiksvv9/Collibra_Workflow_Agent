from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.parse import urljoin

import requests

from src.core.config import Settings


def request_json_design(config: Settings, prompt: str) -> dict[str, Any] | None:
    api_key = _resolved_api_key(config)
    if not api_key:
        return None
    provider = config.openai.provider.lower().strip()
    if provider == "custom_chat_completions":
        text = _custom_chat_completion(config, api_key, prompt)
    else:
        text = _openai_responses_completion(config, api_key, prompt)
    return _extract_json_object(text)


def _custom_chat_completion(config: Settings, api_key: str, prompt: str) -> str:
    url = urljoin(config.openai.base_url.rstrip("/") + "/", config.openai.chat_completions_path.lstrip("/"))
    headers = {
        "Content-Type": "application/json",
        config.openai.api_key_header: f"{config.openai.api_key_prefix}{api_key}",
    }
    payload = {
        "model": config.models.chat_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": config.models.temperature,
        "max_completion_tokens": config.models.max_output_tokens,
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=config.models.request_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            content = message.get("content")
            if isinstance(content, list):
                return "\n".join(str(part.get("text", part)) for part in content)
            if content is not None:
                return str(content)
        if data.get("output_text") is not None:
            return str(data["output_text"])
    return json.dumps(data)


def _openai_responses_completion(config: Settings, api_key: str, prompt: str) -> str:
    from openai import OpenAI

    kwargs: dict[str, Any] = {"timeout": config.models.request_timeout_seconds, "api_key": api_key}
    if config.openai.organization:
        kwargs["organization"] = config.openai.organization
    if config.openai.project:
        kwargs["project"] = config.openai.project
    if config.openai.base_url:
        kwargs["base_url"] = config.openai.base_url
    client = OpenAI(**kwargs)
    response = client.responses.create(
        model=config.models.chat_model,
        input=prompt,
        temperature=config.models.temperature,
        max_output_tokens=config.models.max_output_tokens,
    )
    return response.output_text


def _resolved_api_key(config: Settings) -> str:
    return (
        config.openai.api_key
        or os.getenv(config.openai.api_key_env or "")
        or os.getenv("OPENAI_API_KEY", "")
    ).strip()


def _extract_json_object(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", str(text or ""), re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(0))

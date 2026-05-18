from __future__ import annotations

import json
import os
import re
from dataclasses import asdict
from typing import Any
from urllib.parse import urljoin

import requests

from src.core.config import ChatModelOption, Settings
from src.core.usage_tracker import record_usage


def request_json_design(
    config: Settings,
    prompt: str,
    model_id: str | None = None,
    action: str = "json_design",
) -> dict[str, Any] | None:
    text = request_text_completion(config, prompt, model_id=model_id, action=action)
    if not text:
        return None
    return _extract_json_object(text)


def request_text_completion(
    config: Settings,
    prompt: str,
    model_id: str | None = None,
    action: str = "text_completion",
) -> str | None:
    profile = resolve_model_profile(config, model_id)
    api_key = _resolved_api_key(config, profile)
    if not api_key:
        return None
    provider = (profile.provider or config.openai.provider).lower().strip()
    if provider == "custom_chat_completions":
        text, usage = _custom_chat_completion(config, profile, api_key, prompt)
    elif provider == "custom_messages":
        text, usage = _custom_messages_completion(config, profile, api_key, prompt)
    elif provider == "gemini_generate_content":
        text, usage = _gemini_generate_content(config, profile, api_key, prompt)
    else:
        text, usage = _openai_responses_completion(config, profile, api_key, prompt)
    record_usage(
        action=action,
        provider=provider,
        model=profile.model or config.models.chat_model,
        prompt=prompt,
        completion=text or "",
        usage=usage,
        config=config,
    )
    return text


def resolve_model_profile(config: Settings, model_id: str | None = None) -> ChatModelOption:
    requested = (model_id or "").strip()
    options = list(config.models.available_chat_models or [])
    for option in options:
        if requested and requested in {option.id, option.model}:
            return option
    for option in options:
        if config.models.chat_model in {option.id, option.model}:
            return option
    if options:
        return options[0]
    return ChatModelOption(
        id=config.models.chat_model,
        label=config.models.chat_model,
        provider=config.openai.provider,
        model=config.models.chat_model,
        base_url=config.openai.base_url,
        chat_completions_path=config.openai.chat_completions_path,
        api_key_env=config.openai.api_key_env,
        api_key_header=config.openai.api_key_header,
        api_key_prefix=config.openai.api_key_prefix,
        max_output_tokens=config.models.max_output_tokens,
        temperature=config.models.temperature,
    )


def _custom_chat_completion(
    config: Settings,
    profile: ChatModelOption,
    api_key: str,
    prompt: str,
) -> tuple[str, dict[str, Any]]:
    url = _profile_url(config, profile)
    headers = {
        "Content-Type": "application/json",
        (profile.api_key_header or config.openai.api_key_header): f"{profile.api_key_prefix or config.openai.api_key_prefix}{api_key}",
    }
    payload = {
        "model": profile.model or config.models.chat_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": profile.temperature,
        "max_completion_tokens": profile.max_output_tokens or config.models.max_output_tokens,
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=config.models.request_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    return _extract_text_from_response(data), _usage_from_response(data)


def _custom_messages_completion(
    config: Settings,
    profile: ChatModelOption,
    api_key: str,
    prompt: str,
) -> tuple[str, dict[str, Any]]:
    url = _profile_url(config, profile)
    headers = {
        "Content-Type": "application/json",
        (profile.api_key_header or config.openai.api_key_header): f"{profile.api_key_prefix or config.openai.api_key_prefix}{api_key}",
    }
    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": profile.max_output_tokens or config.models.max_output_tokens,
        "temperature": profile.temperature,
    }
    if profile.model:
        payload["model"] = profile.model
    response = requests.post(url, headers=headers, json=payload, timeout=config.models.request_timeout_seconds)
    response.raise_for_status()
    data = response.json()
    return _extract_text_from_response(data), _usage_from_response(data)


def _gemini_generate_content(
    config: Settings,
    profile: ChatModelOption,
    api_key: str,
    prompt: str,
) -> tuple[str, dict[str, Any]]:
    url = _profile_url(config, profile)
    headers = {
        "Content-Type": "application/json",
        (profile.api_key_header or "x-goog-api-key"): api_key,
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": profile.temperature,
            "maxOutputTokens": profile.max_output_tokens or config.models.max_output_tokens,
        },
    }
    response = requests.post(url, headers=headers, json=payload, timeout=config.models.request_timeout_seconds)
    response.raise_for_status()
    data = response.json()
    return _extract_text_from_response(data), _usage_from_response(data)


def _openai_responses_completion(
    config: Settings,
    profile: ChatModelOption,
    api_key: str,
    prompt: str,
) -> tuple[str, dict[str, Any]]:
    from openai import OpenAI

    kwargs: dict[str, Any] = {"timeout": config.models.request_timeout_seconds, "api_key": api_key}
    if config.openai.organization:
        kwargs["organization"] = config.openai.organization
    if config.openai.project:
        kwargs["project"] = config.openai.project
    if profile.base_url or config.openai.base_url:
        kwargs["base_url"] = profile.base_url or config.openai.base_url
    client = OpenAI(**kwargs)
    response = client.responses.create(
        model=profile.model or config.models.chat_model,
        input=prompt,
        temperature=profile.temperature,
        max_output_tokens=profile.max_output_tokens or config.models.max_output_tokens,
    )
    usage = {}
    if getattr(response, "usage", None):
        try:
            usage = response.usage.model_dump()
        except Exception:
            usage = dict(response.usage)
    return response.output_text, usage


def _resolved_api_key(config: Settings, profile: ChatModelOption) -> str:
    return (
        config.openai.api_key
        or os.getenv(profile.api_key_env or "")
        or os.getenv(config.openai.api_key_env or "")
        or os.getenv("OPENAI_API_KEY", "")
        or os.getenv("AI_GATEWAY_API_KEY", "")
    ).strip()


def _profile_url(config: Settings, profile: ChatModelOption) -> str:
    base_url = (profile.base_url or config.openai.base_url or "").rstrip("/")
    path = (profile.chat_completions_path or config.openai.chat_completions_path or "").lstrip("/")
    return urljoin(base_url + "/", path)


def _extract_text_from_response(data: Any) -> str:
    if not isinstance(data, dict):
        return str(data)
    choices = data.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, list):
            return "\n".join(_content_part_text(part) for part in content)
        if content is not None:
            return str(content)
        if choices[0].get("text") is not None:
            return str(choices[0]["text"])
    content = data.get("content")
    if isinstance(content, list):
        return "\n".join(_content_part_text(part) for part in content)
    if isinstance(content, str):
        return content
    candidates = data.get("candidates") or []
    if candidates:
        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        return "\n".join(_content_part_text(part) for part in parts)
    for key in ("output_text", "completion", "text"):
        if data.get(key) is not None:
            return str(data[key])
    return json.dumps(data)


def _content_part_text(part: Any) -> str:
    if isinstance(part, dict):
        return str(part.get("text") or part.get("content") or part)
    return str(part)


def _usage_from_response(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    usage = data.get("usage") or data.get("usageMetadata") or {}
    if not isinstance(usage, dict):
        return {}
    return {
        "prompt_tokens": usage.get("prompt_tokens") or usage.get("input_tokens") or usage.get("promptTokenCount"),
        "completion_tokens": usage.get("completion_tokens") or usage.get("output_tokens") or usage.get("candidatesTokenCount"),
        "total_tokens": usage.get("total_tokens") or usage.get("totalTokenCount"),
    }


def model_options_payload(config: Settings) -> list[dict[str, Any]]:
    return [
        {
            key: value
            for key, value in asdict(option).items()
            if key not in {"api_key_prefix"}
        }
        for option in (config.models.available_chat_models or [resolve_model_profile(config)])
    ]


def _extract_json_object(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", str(text or ""), re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(0))

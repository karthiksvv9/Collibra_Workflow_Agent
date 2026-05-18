from __future__ import annotations

import hashlib
import math
import os
import re
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        model: str,
        timeout_seconds: int = 90,
        api_key: str = "",
        organization: str = "",
        project: str = "",
        base_url: str = "",
    ) -> None:
        from openai import OpenAI

        self.model = model
        kwargs = {"timeout": timeout_seconds}
        if api_key:
            kwargs["api_key"] = api_key
        if organization:
            kwargs["organization"] = organization
        if project:
            kwargs["project"] = project
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


class HashingEmbeddingProvider(EmbeddingProvider):
    """Deterministic local fallback for tests, demos, and offline development."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[A-Za-z0-9_:-]+", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def default_embedding_provider(
    model: str,
    timeout_seconds: int,
    api_key: str = "",
    api_key_env: str = "OPENAI_API_KEY",
    organization: str = "",
    project: str = "",
    base_url: str = "",
    provider: str = "openai",
    enabled: bool = True,
) -> EmbeddingProvider:
    if provider.lower() == "hashing" or not enabled:
        return HashingEmbeddingProvider()
    resolved_key = api_key or os.getenv(api_key_env or "OPENAI_API_KEY", "")
    if resolved_key:
        return OpenAIEmbeddingProvider(
            model=model,
            timeout_seconds=timeout_seconds,
            api_key=resolved_key,
            organization=organization,
            project=project,
            base_url=base_url,
        )
    return HashingEmbeddingProvider()

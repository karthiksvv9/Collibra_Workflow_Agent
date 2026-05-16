from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.rag.documents import SourceDocument


@dataclass(slots=True)
class Chunk:
    id: str
    source_path: str
    kind: str
    text: str
    metadata: dict[str, Any]


class TextChunker:
    def __init__(self, chunk_size: int = 1400, overlap: int = 220) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: SourceDocument) -> list[Chunk]:
        text = document.text.strip()
        if not text:
            return []
        chunks: list[Chunk] = []
        start = 0
        index = 0
        while start < len(text):
            end = min(len(text), start + self.chunk_size)
            if end < len(text):
                breakpoint = max(text.rfind("\n", start, end), text.rfind(". ", start, end))
                if breakpoint > start + self.chunk_size // 2:
                    end = breakpoint + 1
            body = text[start:end].strip()
            if body:
                chunks.append(
                    Chunk(
                        id=f"{document.path}::{index}",
                        source_path=document.path,
                        kind=document.kind,
                        text=body,
                        metadata={**document.metadata, "chunk_index": index},
                    )
                )
            index += 1
            start = max(end - self.overlap, end if end == len(text) else start + 1)
            if end == len(text):
                break
        return chunks


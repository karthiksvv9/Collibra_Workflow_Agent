from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.rag.chunker import Chunk


@dataclass(slots=True)
class SearchResult:
    chunk: Chunk
    score: float


class SQLiteVectorStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    source_path TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    text TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_path)")

    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        rows = [
            (
                chunk.id,
                chunk.source_path,
                chunk.kind,
                chunk.text,
                json.dumps(chunk.metadata, sort_keys=True),
                json.dumps(embedding),
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO chunks(id, source_path, kind, text, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_path=excluded.source_path,
                    kind=excluded.kind,
                    text=excluded.text,
                    metadata=excluded.metadata,
                    embedding=excluded.embedding
                """,
                rows,
            )

    def search(self, query_embedding: list[float], limit: int = 8) -> list[SearchResult]:
        results: list[SearchResult] = []
        with self._connect() as conn:
            rows = conn.execute("SELECT id, source_path, kind, text, metadata, embedding FROM chunks").fetchall()
        for row in rows:
            embedding = json.loads(row[5])
            score = cosine_similarity(query_embedding, embedding)
            chunk = Chunk(
                id=row[0],
                source_path=row[1],
                kind=row[2],
                text=row[3],
                metadata=json.loads(row[4]),
            )
            results.append(SearchResult(chunk=chunk, score=score))
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
        return int(row[0])

    def source_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(DISTINCT source_path) FROM chunks").fetchone()
        return int(row[0])

    def kind_counts(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute("SELECT kind, COUNT(*) FROM chunks GROUP BY kind").fetchall()
        return {str(kind): int(count) for kind, count in rows}

    def delete_sources(self, sources: Iterable[str]) -> None:
        with self._connect() as conn:
            conn.executemany("DELETE FROM chunks WHERE source_path = ?", [(source,) for source in sources])


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    dot = sum(left[i] * right[i] for i in range(size))
    left_norm = math.sqrt(sum(value * value for value in left[:size])) or 1.0
    right_norm = math.sqrt(sum(value * value for value in right[:size])) or 1.0
    return dot / (left_norm * right_norm)

from __future__ import annotations

from pathlib import Path

from src.core.config import load_settings
from src.rag.embeddings import HashingEmbeddingProvider
from src.rag.engine import RAGEngine
from src.rag.vector_store import SQLiteVectorStore


def test_rag_engine_ingests_and_retrieves(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "standard.md").write_text(
        "Collibra script tasks must include explicit imports and can use assetApi in workflow context.",
        encoding="utf-8",
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
paths:
  docs_dir: "{docs.as_posix()}"
  jars_dir: "{(tmp_path / "jars").as_posix()}"
  output_dir: "{(tmp_path / "output").as_posix()}"
  vector_store: "{(tmp_path / "vectors.sqlite3").as_posix()}"
runtime:
  chunk_size: 200
  chunk_overlap: 20
""",
        encoding="utf-8",
    )
    settings = load_settings(config_path)
    engine = RAGEngine(
        settings,
        embedding_provider=HashingEmbeddingProvider(64),
        store=SQLiteVectorStore(tmp_path / "vectors.sqlite3"),
    )

    report = engine.ingest()
    context = engine.retrieve("How should Collibra script tasks import classes?")

    assert report.documents == 1
    assert report.chunks >= 1
    assert context.results
    assert "explicit imports" in context.render()


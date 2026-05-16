from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from src.core.config import Settings, settings
from src.core.logging import get_logger
from src.rag.chunker import Chunk, TextChunker
from src.rag.documents import SourceDocument, discover_documents, load_document
from src.rag.embeddings import EmbeddingProvider, default_embedding_provider
from src.rag.relation_mapper import RelationGraph, RelationMapper
from src.rag.vector_store import SQLiteVectorStore, SearchResult


logger = get_logger(__name__)


@dataclass(slots=True)
class IngestionReport:
    documents: int
    chunks: int
    relations: int
    vector_count: int
    warnings: list[str]


@dataclass(slots=True)
class RAGAnswerContext:
    question: str
    results: list[SearchResult]
    relation_graph: RelationGraph

    def render(self) -> str:
        parts = [f"Question: {self.question}", "Retrieved context:"]
        for result in self.results:
            parts.append(
                f"- score={result.score:.3f} source={result.chunk.source_path} "
                f"kind={result.chunk.kind}\n{result.chunk.text}"
            )
        if self.relation_graph.relations:
            parts.append("Semantic relations:")
            for relation in self.relation_graph.relations[:50]:
                parts.append(
                    f"- {relation.source} --{relation.relation_type}--> {relation.target} "
                    f"({relation.evidence}, confidence={relation.confidence:.2f})"
                )
        return "\n\n".join(parts)


class RAGEngine:
    def __init__(
        self,
        config: Settings = settings,
        embedding_provider: EmbeddingProvider | None = None,
        store: SQLiteVectorStore | None = None,
    ) -> None:
        self.config = config
        self.chunker = TextChunker(config.runtime.chunk_size, config.runtime.chunk_overlap)
        self.embeddings = embedding_provider or default_embedding_provider(
            config.models.embedding_model,
            config.models.request_timeout_seconds,
            api_key=config.openai.api_key,
            organization=config.openai.organization,
            project=config.openai.project,
            base_url=config.openai.base_url,
        )
        self.store = store or SQLiteVectorStore(config.paths.vector_store)
        self.mapper = RelationMapper(
            uuid_columns=config.collibra.uuid_columns,
            role_columns=config.collibra.role_columns,
            sample_rows=config.runtime.relation_sample_rows,
        )
        self.relation_graph = RelationGraph()

    def ingest(self, root: str | Path | None = None) -> IngestionReport:
        root_path = Path(root or self.config.paths.docs_dir)
        paths = discover_documents(root_path)
        warnings: list[str] = []
        if not paths:
            return IngestionReport(0, 0, 0, self.store.count(), ["No documents found for ingestion."])

        documents: list[SourceDocument] = []
        max_workers = max(1, min(self.config.runtime.max_workers, len(paths)))
        executor_cls = ProcessPoolExecutor if self.config.runtime.use_multiprocessing else ThreadPoolExecutor
        with executor_cls(max_workers=max_workers) as pool:
            futures = {pool.submit(load_document, path): path for path in paths}
            for future in as_completed(futures):
                path = futures[future]
                try:
                    documents.append(future.result())
                except Exception as exc:  # pragma: no cover - defensive around third-party parsers
                    warnings.append(f"{path}: {exc}")

        all_chunks: list[Chunk] = []
        for document in documents:
            all_chunks.extend(self.chunker.chunk(document))
            warning = document.metadata.get("warning")
            if warning:
                warnings.append(f"{document.path}: {warning}")

        for batch in _batched(all_chunks, self.config.runtime.ingestion_batch_size):
            vectors = self.embeddings.embed([chunk.text for chunk in batch])
            self.store.upsert(batch, vectors)

        graph = RelationGraph()
        if self.config.runtime.use_multithreading:
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(self.mapper.map_path, path): path for path in paths}
                for future in as_completed(futures):
                    path = futures[future]
                    try:
                        graph.merge(future.result())
                    except Exception as exc:  # pragma: no cover
                        warnings.append(f"Relation mapping failed for {path}: {exc}")
        else:
            for path in paths:
                try:
                    graph.merge(self.mapper.map_path(path))
                except Exception as exc:  # pragma: no cover
                    warnings.append(f"Relation mapping failed for {path}: {exc}")
        self.relation_graph = graph

        return IngestionReport(
            documents=len(documents),
            chunks=len(all_chunks),
            relations=len(graph.relations),
            vector_count=self.store.count(),
            warnings=warnings,
        )

    def retrieve(self, question: str, limit: int = 8) -> RAGAnswerContext:
        query_embedding = self.embeddings.embed([question])[0]
        return RAGAnswerContext(
            question=question,
            results=self.store.search(query_embedding, limit=limit),
            relation_graph=self.relation_graph,
        )


def _batched(values: list[Chunk], size: int) -> list[list[Chunk]]:
    return [values[index : index + size] for index in range(0, len(values), max(1, size))]

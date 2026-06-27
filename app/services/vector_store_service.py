from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.core.config import settings
from app.core.logger import logger
from app.services.chroma_client import get_chroma_client
from app.services.chunking_service import TextChunk
from app.services.embedding_service import EmbeddingService


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    source: str
    chunk_index: int
    score: float
    metadata: dict[str, Any]


class VectorStoreService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self._client = get_chroma_client()
        self._collection = self._client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def index_document(self, document_id: str, chunks: list[TextChunk]) -> int:
        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_service.embed(texts)
        ids = [f"{document_id}:{chunk.chunk_index}:{uuid4().hex[:8]}" for chunk in chunks]
        metadatas = [
            {
                "document_id": document_id,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            }
            for chunk in chunks
        ]

        self._collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info("Indexed {} chunks for document {}", len(chunks), document_id)
        return len(chunks)

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        limit = top_k or settings.top_k
        query_embedding = self.embedding_service.embed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved: list[RetrievedChunk] = []
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
            score = 1.0 - float(distance)
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=text,
                    source=metadata.get("source", "unknown"),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    score=score,
                    metadata=metadata,
                )
            )
        return retrieved

    def document_count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        self._client.delete_collection(settings.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

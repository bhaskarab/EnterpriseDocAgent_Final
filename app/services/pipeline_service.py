from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService
from app.utils.file_helpers import file_hash, safe_filename


@dataclass
class DocumentPipeline:
    ingestion: IngestionService
    chunking: ChunkingService
    vector_store: VectorStoreService

    def process_upload(self, filename: str, content: bytes) -> dict:
        safe_name = safe_filename(filename)
        document_id = f"{safe_name}-{file_hash(content)}"
        text = self.ingestion.ingest_bytes(filename, content)
        chunks = self.chunking.chunk_text(text, source=safe_name)
        indexed = self.vector_store.index_document(document_id, chunks)
        return {
            "document_id": document_id,
            "filename": safe_name,
            "characters": len(text),
            "chunks_indexed": indexed,
        }


@lru_cache
def get_pipeline() -> DocumentPipeline:
    embedding = EmbeddingService()
    vector_store = VectorStoreService(embedding_service=embedding)
    return DocumentPipeline(
        ingestion=IngestionService(),
        chunking=ChunkingService(),
        vector_store=vector_store,
    )


@lru_cache
def get_rag_service() -> RAGService:
    pipeline = get_pipeline()
    return RAGService(vector_store=pipeline.vector_store)

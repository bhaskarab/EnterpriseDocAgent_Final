from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logger import logger
from app.services.citation_service import Citation, CitationService
from app.services.vector_store_service import RetrievedChunk, VectorStoreService


class RAGService:
    def __init__(
        self,
        vector_store: VectorStoreService | None = None,
        citation_service: CitationService | None = None,
    ) -> None:
        self.vector_store = vector_store or VectorStoreService()
        self.citation_service = citation_service or CitationService()

    def answer(self, question: str, top_k: int | None = None) -> dict:
        chunks = self.vector_store.search(question, top_k=top_k)
        citations = self.citation_service.build_citations(chunks)

        if not chunks:
            return {
                "answer": "No relevant documents were found. Upload enterprise documents first.",
                "citations": [],
                "context_used": 0,
                "llm_used": False,
            }

        llm_answer = self._generate_with_ollama(question, chunks)
        if llm_answer:
            formatted = self.citation_service.format_answer_with_citations(llm_answer, citations)
            return {
                "answer": formatted,
                "citations": [c.to_dict() for c in citations],
                "context_used": len(chunks),
                "llm_used": True,
            }

        fallback = self._extractive_answer(question, chunks)
        formatted = self.citation_service.format_answer_with_citations(fallback, citations)
        return {
            "answer": formatted,
            "citations": [c.to_dict() for c in citations],
            "context_used": len(chunks),
            "llm_used": False,
        }

    def _generate_with_ollama(self, question: str, chunks: list[RetrievedChunk]) -> str | None:
        context = "\n\n".join(
            f"[{idx}] Source: {chunk.source}\n{chunk.text}"
            for idx, chunk in enumerate(chunks, start=1)
        )
        prompt = (
            "You are an enterprise document assistant. Answer the question using ONLY the provided context. "
            "If the answer is not in the context, say you cannot find it.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )

        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
                timeout=60.0,
            )
            response.raise_for_status()
            payload = response.json()
            answer = payload.get("response", "").strip()
            return answer or None
        except Exception as exc:
            logger.warning("Ollama unavailable, using extractive fallback: {}", exc)
            return None

    def _extractive_answer(self, question: str, chunks: list[RetrievedChunk]) -> str:
        keywords = {word.lower() for word in question.split() if len(word) > 3}
        best = chunks[0]
        best_score = -1

        for chunk in chunks:
            words = chunk.text.lower().split()
            overlap = sum(1 for word in words if word in keywords)
            score = overlap + chunk.score
            if score > best_score:
                best_score = score
                best = chunk

        return (
            f"Based on the indexed documents, the most relevant passage states: {best.text[:600]}"
            + ("..." if len(best.text) > 600 else "")
        )

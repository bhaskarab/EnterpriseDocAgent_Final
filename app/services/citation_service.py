from dataclasses import dataclass

from app.services.vector_store_service import RetrievedChunk


@dataclass
class Citation:
    index: int
    source: str
    chunk_index: int
    excerpt: str
    score: float

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "source": self.source,
            "chunk_index": self.chunk_index,
            "excerpt": self.excerpt,
            "score": round(self.score, 4),
            "reference": f"[{self.index}] {self.source} (chunk {self.chunk_index})",
        }


class CitationService:
    def build_citations(self, chunks: list[RetrievedChunk], excerpt_len: int = 200) -> list[Citation]:
        citations: list[Citation] = []
        for idx, chunk in enumerate(chunks, start=1):
            excerpt = chunk.text[:excerpt_len].replace("\n", " ").strip()
            if len(chunk.text) > excerpt_len:
                excerpt += "..."
            citations.append(
                Citation(
                    index=idx,
                    source=chunk.source,
                    chunk_index=chunk.chunk_index,
                    excerpt=excerpt,
                    score=chunk.score,
                )
            )
        return citations

    def format_answer_with_citations(self, answer: str, citations: list[Citation]) -> str:
        if not citations:
            return answer

        references = "\n".join(citation.to_dict()["reference"] for citation in citations)
        return f"{answer.strip()}\n\nSources:\n{references}"

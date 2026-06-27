from dataclasses import dataclass

from app.core.config import settings


@dataclass
class TextChunk:
    text: str
    chunk_index: int
    source: str
    start_char: int
    end_char: int


class ChunkingService:
    def chunk_text(
        self,
        text: str,
        source: str = "unknown",
        size: int | None = None,
        overlap: int | None = None,
    ) -> list[TextChunk]:
        chunk_size = size or settings.chunk_size
        chunk_overlap = overlap or settings.chunk_overlap
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        normalized = text.strip()
        if not normalized:
            return []

        chunks: list[TextChunk] = []
        step = max(1, chunk_size - chunk_overlap)
        index = 0
        position = 0

        while position < len(normalized):
            end = min(position + chunk_size, len(normalized))
            chunk = normalized[position:end].strip()
            if chunk:
                chunks.append(
                    TextChunk(
                        text=chunk,
                        chunk_index=index,
                        source=source,
                        start_char=position,
                        end_char=end,
                    )
                )
                index += 1
            position += step

        return chunks

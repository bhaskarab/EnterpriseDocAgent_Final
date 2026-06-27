from __future__ import annotations

import hashlib
from typing import Any

from app.core.config import settings
from app.core.logger import logger


class EmbeddingService:
    def __init__(self) -> None:
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model: {}", settings.embedding_model)
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if settings.testing:
            return [self._mock_vector(text) for text in texts]

        model = self._load_model()
        vectors = model.encode(texts, show_progress_bar=False)
        return [vector.tolist() for vector in vectors]

    def embed_query(self, query: str) -> list[float]:
        return self.embed([query])[0]

    @staticmethod
    def _mock_vector(text: str, dim: int = 384) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        while len(values) < dim:
            for byte in digest:
                values.append((byte / 255.0) * 2 - 1)
                if len(values) == dim:
                    break
            digest = hashlib.sha256(digest).digest()
        return values

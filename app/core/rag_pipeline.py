from app.services.rag_service import RAGService


class RAGPipeline:
    """Standalone RAG pipeline (Guideline 7). The active query path also uses LangGraph agents."""

    def __init__(self, rag_service: RAGService | None = None) -> None:
        self.rag_service = rag_service or RAGService()

    def query(self, user_question: str) -> dict:
        return self.rag_service.answer(user_question)

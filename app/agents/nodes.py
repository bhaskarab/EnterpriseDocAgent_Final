from app.agents.state import AgentState
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService


def route_query(state: AgentState) -> AgentState:
    question = state["question"].lower()
    if any(word in question for word in ("summarize", "summary", "overview")):
        query_type = "summary"
    elif any(word in question for word in ("compare", "difference", "versus", "vs")):
        query_type = "comparison"
    elif any(word in question for word in ("list", "enumerate", "show all")):
        query_type = "listing"
    else:
        query_type = "factual"
    return {**state, "query_type": query_type}


def retrieve_context(state: AgentState, vector_store: VectorStoreService) -> AgentState:
    chunks = vector_store.search(state["question"])
    serialized = [
        {
            "chunk_id": chunk.chunk_id,
            "text": chunk.text,
            "source": chunk.source,
            "chunk_index": chunk.chunk_index,
            "score": chunk.score,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]
    return {**state, "retrieved_chunks": serialized}


def synthesize_answer(state: AgentState, rag_service: RAGService) -> AgentState:
    result = rag_service.answer(state["question"])
    return {
        **state,
        "answer": result["answer"],
        "citations": result["citations"],
        "context_used": result["context_used"],
        "llm_used": result["llm_used"],
    }

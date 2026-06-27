from langgraph.graph import END, START, StateGraph

from app.agents.nodes import retrieve_context, route_query, synthesize_answer
from app.agents.state import AgentState
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService


def build_agent_graph(
    vector_store: VectorStoreService | None = None,
    rag_service: RAGService | None = None,
):
    store = vector_store or VectorStoreService()
    rag = rag_service or RAGService(vector_store=store)

    graph = StateGraph(AgentState)
    graph.add_node("router", route_query)
    graph.add_node("retriever", lambda state: retrieve_context(state, store))
    graph.add_node("synthesizer", lambda state: synthesize_answer(state, rag))

    graph.add_edge(START, "router")
    graph.add_edge("router", "retriever")
    graph.add_edge("retriever", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()


def run_agent(question: str, vector_store: VectorStoreService | None = None) -> dict:
    workflow = build_agent_graph(vector_store=vector_store)
    final_state = workflow.invoke({"question": question})
    return {
        "question": question,
        "query_type": final_state.get("query_type", "factual"),
        "answer": final_state.get("answer", ""),
        "citations": final_state.get("citations", []),
        "context_used": final_state.get("context_used", 0),
        "llm_used": final_state.get("llm_used", False),
    }

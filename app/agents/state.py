from typing import TypedDict


class AgentState(TypedDict, total=False):
    question: str
    query_type: str
    retrieved_chunks: list
    citations: list
    answer: str
    llm_used: bool
    context_used: int

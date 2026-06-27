from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.graph import run_agent
from app.services.pipeline_service import get_pipeline
from app.utils.guardrails import GuardrailsService
from app.utils.validator import InputValidator

router = APIRouter(prefix="/query", tags=["query"])
validator = InputValidator()
guardrails = GuardrailsService()


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class CitationModel(BaseModel):
    index: int
    source: str
    chunk_index: int
    excerpt: str
    score: float
    reference: str


class QuestionResponse(BaseModel):
    question: str
    query_type: str
    answer: str
    citations: list[CitationModel]
    context_used: int
    llm_used: bool
    is_grounded: bool
    warning: str | None = None


@router.post("/ask", response_model=QuestionResponse)
def ask_question(payload: QuestionRequest):
    validation = validator.validate_query(payload.question)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.error_message)

    question = payload.question.strip()
    pipeline = get_pipeline()
    if pipeline.vector_store.document_count() == 0:
        raise HTTPException(
            status_code=404,
            detail="No documents indexed yet. Upload documents before asking questions.",
        )

    result = run_agent(question, vector_store=pipeline.vector_store)
    validated = guardrails.validate_response(result["answer"], question)
    formatted = guardrails.format_response(validated)

    return QuestionResponse(
        question=question,
        query_type=result.get("query_type", "factual"),
        answer=formatted,
        citations=result.get("citations", []),
        context_used=result.get("context_used", 0),
        llm_used=result.get("llm_used", False),
        is_grounded=validated["is_grounded"],
        warning=validated["warning"],
    )

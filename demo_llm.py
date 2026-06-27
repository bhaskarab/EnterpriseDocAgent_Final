#!/usr/bin/env python3
"""Demonstrate the Ollama LLM + RAG path for capstone evaluation."""

import sys

from loguru import logger

from app.agents.graph import run_agent
from app.services.pipeline_service import get_pipeline
from app.utils.ollama_health import check_ollama_status


logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
)

DEMO_QUESTION = "What file formats does EnterpriseDocAgent support?"


def main() -> int:
    logger.info("EnterpriseDocAgent — LLM evaluation demo")
    logger.info("=" * 50)

    ollama = check_ollama_status()
    if not ollama["reachable"]:
        logger.error("Ollama is not running. Start it with: ollama serve")
        logger.error("Then pull the model: ollama pull llama3")
        return 1

    if not ollama["model_available"]:
        logger.error("Model '{}' not found. Run: ollama pull {}", ollama["model"], ollama["model"])
        return 1

    logger.success("Ollama reachable at {}", ollama["base_url"])
    logger.success("Model available: {}", ollama["model"])

    pipeline = get_pipeline()
    if pipeline.vector_store.document_count() == 0:
        logger.info("No indexed documents found. Ingesting sample data...")
        from ingest_docs import ingest_all_documents

        ingest_all_documents()

    logger.info("Asking: {}", DEMO_QUESTION)
    result = run_agent(DEMO_QUESTION, vector_store=pipeline.vector_store)

    logger.info("Query type: {}", result.get("query_type"))
    logger.info("Context chunks used: {}", result.get("context_used"))
    logger.info("LLM used: {}", result.get("llm_used"))

    if result.get("llm_used"):
        logger.success("LLM path verified — answer generated via Ollama + RAG")
    else:
        logger.warning("LLM was NOT used — check Ollama logs and model name in .env")
        return 1

    print("\n--- Answer ---")
    print(result.get("answer", ""))
    print("--------------\n")

    citations = result.get("citations", [])
    if citations:
        logger.info("Citations returned: {}", len(citations))
        for citation in citations[:3]:
            logger.info("  {}", citation.get("reference"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

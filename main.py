import sys

import httpx
from loguru import logger

from app.core.config import settings
from app.utils.ollama_health import check_ollama_status


logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
)


def main() -> None:
    logger.info("Starting {} v{}", settings.app_name, settings.app_version)
    logger.info("Embedding model: {}", settings.embedding_model)
    logger.info("ChromaDB path: {}", settings.chroma_path)
    logger.info("Debug mode: {}", settings.debug)
    logger.info("Ollama model: {}", settings.ollama_model)

    ollama = check_ollama_status()
    if ollama["reachable"] and ollama["model_available"]:
        logger.success("Ollama LLM path ready at {} (model: {})", ollama["base_url"], settings.ollama_model)
    elif ollama["reachable"]:
        logger.warning(
            "Ollama is running but model '{}' not found. Run: ollama pull {}",
            settings.ollama_model,
            settings.ollama_model,
        )
    else:
        logger.warning(
            "Ollama not reachable at {}. Extractive fallback will be used. Error: {}",
            ollama["base_url"],
            ollama.get("error", "unknown"),
        )

    logger.success("Configuration loaded successfully!")
    logger.success("{} is ready!", settings.app_name)
    logger.info("Run `python ingest_docs.py` then `streamlit run streamlit_app.py`")
    logger.info("For evaluator demo: `python demo_llm.py`")


if __name__ == "__main__":
    main()

import os
import sys

from loguru import logger

from app.services.document_processor import DocumentProcessor
from app.services.pipeline_service import get_pipeline


logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
)


def ingest_all_documents(data_folder: str = "data/") -> None:
    processor = DocumentProcessor()
    pipeline = get_pipeline()

    success_count = 0
    error_count = 0
    skipped_count = 0
    total_chunks = 0

    logger.info("Starting ingestion from folder: {}", data_folder)

    for root, _, files in os.walk(data_folder):
        for filename in files:
            if filename.startswith(".") or filename.endswith(".gitkeep"):
                continue

            file_path = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1].lower()
            if extension not in processor.SUPPORTED_FORMATS:
                skipped_count += 1
                continue

            try:
                content = open(file_path, "rb").read()
                text = processor.process_bytes(filename, content)
                if not text.strip():
                    logger.warning("Empty file skipped: {}", filename)
                    skipped_count += 1
                    continue

                result = pipeline.process_upload(filename, content)
                total_chunks += result["chunks_indexed"]
                success_count += 1
                logger.success("Ingested: {}", filename)
            except Exception as exc:
                logger.error("Error processing {}: {}", filename, exc)
                error_count += 1

    logger.info("=" * 50)
    logger.success("Ingestion Complete!")
    logger.info("Successfully ingested : {} files", success_count)
    logger.info("Skipped              : {} files", skipped_count)
    logger.info("Errors               : {} files", error_count)
    logger.info("Total chunks indexed : {}", total_chunks)


if __name__ == "__main__":
    ingest_all_documents()

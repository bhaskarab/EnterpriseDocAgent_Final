from app.services.ingestion_service import IngestionService


class DocumentProcessor:
    SUPPORTED_FORMATS = list(IngestionService.SUPPORTED)

    def __init__(self) -> None:
        self.ingestion = IngestionService()

    def process(self, file_path: str) -> str:
        return self.ingestion.ingest_file(file_path)

    def process_bytes(self, filename: str, content: bytes) -> str:
        return self.ingestion.ingest_bytes(filename, content)

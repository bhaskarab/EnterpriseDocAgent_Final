import csv
import io
import json
from pathlib import Path

import pandas as pd
import yaml
from pypdf import PdfReader

from app.core.logger import logger


class IngestionService:
    """Load text from supported enterprise document formats."""

    SUPPORTED = {".txt", ".pdf", ".csv", ".xlsx", ".json", ".yaml", ".yml", ".md"}

    def ingest_bytes(self, filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in self.SUPPORTED:
            raise ValueError(
                f"Unsupported file type '{suffix}'. Supported: {', '.join(sorted(self.SUPPORTED))}"
            )

        loaders = {
            ".txt": self._load_text,
            ".pdf": self._load_pdf,
            ".csv": self._load_csv,
            ".xlsx": self._load_xlsx,
            ".json": self._load_json,
            ".yaml": self._load_yaml,
            ".yml": self._load_yaml,
            ".md": self._load_text,
        }
        text = loaders[suffix](content)
        logger.info("Ingested {} ({} chars)", filename, len(text))
        return text.strip()

    def ingest_file(self, path: str | Path) -> str:
        file_path = Path(path)
        return self.ingest_bytes(file_path.name, file_path.read_bytes())

    def _load_text(self, content: bytes) -> str:
        return content.decode("utf-8", errors="ignore")

    def _load_pdf(self, content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    def _load_csv(self, content: bytes) -> str:
        decoded = content.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(decoded))
        rows = [" | ".join(cell.strip() for cell in row if cell) for row in reader if any(row)]
        return "\n".join(rows)

    def _load_xlsx(self, content: bytes) -> str:
        frames = pd.read_excel(io.BytesIO(content), sheet_name=None)
        sections: list[str] = []
        for sheet_name, frame in frames.items():
            sections.append(f"Sheet: {sheet_name}\n{frame.to_string(index=False)}")
        return "\n\n".join(sections)

    def _load_json(self, content: bytes) -> str:
        payload = json.loads(content.decode("utf-8", errors="ignore"))
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def _load_yaml(self, content: bytes) -> str:
        payload = yaml.safe_load(content.decode("utf-8", errors="ignore"))
        return yaml.safe_dump(payload, sort_keys=False)

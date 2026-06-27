from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "EnterpriseDocAgent"
    app_version: str = "1.0.0"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_path: str = "data/chroma"
    upload_dir: str = "data/uploads"
    collection_name: str = "enterprise_documents"
    api_base_url: str = "http://localhost:8000"
    testing: bool = False

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def chroma_directory(self) -> Path:
        path = Path(self.chroma_path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()

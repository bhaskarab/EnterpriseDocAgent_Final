from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.services.pipeline_service import get_pipeline
from app.utils.validator import InputValidator

router = APIRouter(prefix="/documents", tags=["documents"])
validator = InputValidator()


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    characters: int
    chunks_indexed: int
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    content = await file.read()
    validation = validator.validate_file_bytes(file.filename, content)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.error_message)

    upload_path = settings.upload_path / file.filename
    upload_path.write_bytes(content)

    try:
        result = get_pipeline().process_upload(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(
        **result,
        message=f"Successfully indexed {result['chunks_indexed']} chunks",
    )


@router.get("/stats")
def document_stats():
    pipeline = get_pipeline()
    return {
        "indexed_chunks": pipeline.vector_store.document_count(),
        "upload_directory": str(Path(settings.upload_dir).resolve()),
    }

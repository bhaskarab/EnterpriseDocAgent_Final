from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ask import router as ask_router
from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.core.config import settings
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.chroma_directory.mkdir(parents=True, exist_ok=True)
    logger.info("{} API started", settings.app_name)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Enterprise document intelligence platform with RAG and multi-agent orchestration",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(ask_router)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "upload": "/documents/upload",
        "ask": "/query/ask",
    }

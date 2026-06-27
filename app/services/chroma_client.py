"""Thread-safe singleton ChromaDB client.

ChromaDB's SharedSystemClient is not safe under concurrent initialization.
Streamlit can trigger parallel imports/reruns that cause KeyError on the
persist path (e.g. 'data/chroma').
"""

from __future__ import annotations

import threading

import chromadb
from chromadb.api import ClientAPI

from app.core.config import settings

_client: ClientAPI | None = None
_init_lock = threading.Lock()


def get_chroma_client() -> ClientAPI:
    global _client
    if _client is not None:
        return _client

    with _init_lock:
        if _client is None:
            chroma_path = str(settings.chroma_directory.resolve())
            _client = chromadb.PersistentClient(path=chroma_path)
        return _client

import hashlib
import re
from pathlib import Path


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w.\- ]", "_", name.strip())
    return cleaned or "document"


def file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:16]


def detect_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")

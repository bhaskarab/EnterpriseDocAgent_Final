from pathlib import Path

from loguru import logger

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger.add(LOG_DIR / "application.log", rotation="10 MB", retention="7 days")

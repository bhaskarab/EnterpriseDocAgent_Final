import httpx

from app.core.config import settings


def check_ollama_status() -> dict:
    """Check whether Ollama is reachable and the configured model is available."""
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5.0)
        response.raise_for_status()
        models = [item.get("name", "") for item in response.json().get("models", [])]
        model_available = any(
            name == settings.ollama_model or name.startswith(f"{settings.ollama_model}:")
            for name in models
        )
        return {
            "reachable": True,
            "model": settings.ollama_model,
            "model_available": model_available,
            "available_models": models,
            "base_url": settings.ollama_base_url,
        }
    except Exception as exc:
        return {
            "reachable": False,
            "model": settings.ollama_model,
            "model_available": False,
            "available_models": [],
            "base_url": settings.ollama_base_url,
            "error": str(exc),
        }

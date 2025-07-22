import logging
from typing import List

import httpx
from fastapi import HTTPException, status

from config import settings

logger = logging.getLogger(settings.app_name)


async def get_embedding(text: str) -> List[float]:
    """Get embedding from Ollama using the configured embedding model."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={"model": settings.ollama_embedding_model, "prompt": text},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["embedding"]
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate embedding: {str(e)}",
        )


async def get_summary(text: str) -> str:
    """Get summary from Ollama using the configured summary model."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_summary_model,
                    "prompt": (f"Summarize the following text concisely:\n\n{text}"),
                    "stream": False,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["response"]
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return text[:500] + "..." if len(text) > 500 else text

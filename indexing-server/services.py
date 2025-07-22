import logging
import os
from typing import List

import httpx
from fastapi import HTTPException, status

from config import settings

logger = logging.getLogger(settings.app_name)


def read_file_content(file_path: str) -> str:
    """
    Read content from a file path.

    Args:
        file_path: Path to the file to read

    Returns:
        The file content as a string

    Raises:
        HTTPException: If file cannot be read or doesn't exist
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}",
            )

        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a file: {file_path}",
            )

        # Try to read the file with different encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    content = file.read()
                    logger.debug(
                        f"Successfully read file {file_path} with encoding {encoding}"
                    )
                    return content
            except UnicodeDecodeError:
                continue

        # If all encodings fail, try binary mode and decode with error handling
        try:
            with open(file_path, "rb") as file:
                content_bytes = file.read()
                content = content_bytes.decode("utf-8", errors="replace")
                logger.warning(f"Read file {file_path} with error replacement")
                return content
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file {file_path}: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading file {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}",
        )


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

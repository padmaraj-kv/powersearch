import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from config import settings
from database import search_embeddings, delete_file_embeddings, upsert_file_embedding
from models import (
    QueryRequest,
    QueryResponse,
    UpsertRequest,
    UpsertResponse,
    DeleteRequest,
    DeleteResponse,
)
from services import get_embedding, get_summary, read_file_content

logger = logging.getLogger(settings.app_name)

# Create router
router = APIRouter()


@router.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "message": "Indexing Server is running",
        "version": settings.api_version,
        "status": "healthy",
    }


@router.post("/query", response_model=List[QueryResponse], tags=["Search"])
async def query_embeddings(request: QueryRequest):
    """
    Vector search endpoint - returns array of file IDs and paths.
    """
    try:
        logger.info(f"Processing search query: '{request.text[:100]}...'")

        # Get embedding for the query text
        query_embedding = await get_embedding(request.text)

        # Search in Qdrant using database function
        search_results = search_embeddings(query_embedding, request.limit)

        # Format response
        results = []
        for result in search_results:
            results.append(
                QueryResponse(
                    file_id=result.payload["file_id"],
                    file_path=result.payload["file_path"],
                    score=result.score,
                )
            )

        logger.info(f"Search completed: {len(results)} results found")
        return results

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )


@router.post("/upsert", response_model=UpsertResponse, tags=["Indexing"])
@router.put("/upsert", response_model=UpsertResponse, tags=["Indexing"])
async def upsert_embedding_endpoint(request: UpsertRequest):
    """
    Upsert endpoint - creates or updates embeddings for a file.
    Automatically reads file content from file_path and generates summary.
    """
    try:
        logger.info(f"Processing upsert for file: {request.file_id}")

        # Read file content from file_path
        file_content = read_file_content(request.file_path)
        logger.debug(
            f"Read {len(file_content)} characters from file: {request.file_path}"
        )

        # Generate summary from file content
        summary = await get_summary(file_content)
        logger.debug(f"Generated summary for {request.file_id}: {summary[:100]}...")

        # Generate embedding from summary
        embedding = await get_embedding(summary)

        # Upsert the file embedding using database function
        status_msg = upsert_file_embedding(
            file_id=request.file_id,
            file_path=request.file_path,
            embedding=embedding,
            summary=summary,
        )

        return UpsertResponse(
            message=f"File embedding {status_msg} successfully",
            file_id=request.file_id,
            status=status_msg,
        )

    except Exception as e:
        logger.error(f"Upsert error for file {request.file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upsert failed: {str(e)}",
        )


@router.delete("/delete", response_model=DeleteResponse, tags=["Indexing"])
async def delete_embedding_endpoint(request: DeleteRequest):
    """
    Delete endpoint - removes embeddings for a file.
    """
    try:
        logger.info(f"Deleting embeddings for file: {request.file_id}")

        # Delete all points with the given file_id using database function
        delete_file_embeddings(request.file_id)

        logger.info(f"Successfully deleted embeddings for file: {request.file_id}")
        return DeleteResponse(
            message="File embeddings deleted successfully",
            file_id=request.file_id,
            status="deleted",
        )

    except Exception as e:
        logger.error(f"Delete error for file {request.file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}",
        )

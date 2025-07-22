import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status
from qdrant_client import models

from config import settings
from database import qdrant_client
from models import (
    QueryRequest,
    QueryResponse,
    UpsertRequest,
    UpsertResponse,
    DeleteRequest,
    DeleteResponse,
)
from services import get_embedding, get_summary

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

        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=settings.qdrant_collection_name,
            query_vector=query_embedding,
            limit=request.limit,
        )

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
async def upsert_embedding(request: UpsertRequest):
    """
    Upsert endpoint - creates or updates embeddings for a file.
    """
    try:
        logger.info(f"Processing upsert for file: {request.file_id}")

        # Get content summary if content is provided
        if request.content:
            summary = await get_summary(request.content)
            embedding_text = summary
            logger.debug(f"Generated summary for {request.file_id}: {summary[:100]}...")
        else:
            # If no content provided, use file_path as placeholder text
            embedding_text = f"File: {request.file_path}"
            logger.debug(f"Using file path as embedding text for {request.file_id}")

        # Generate embedding
        embedding = await get_embedding(embedding_text)

        # Check if file already exists by searching for the file_id
        existing_points = qdrant_client.search(
            collection_name=settings.qdrant_collection_name,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_id", match=models.MatchValue(value=request.file_id)
                    )
                ]
            ),
            limit=1,
        )

        # Prepare point data
        point_data = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "file_id": request.file_id,
                "file_path": request.file_path,
                "summary": embedding_text,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        # If exists, delete old embeddings first
        if existing_points:
            qdrant_client.delete(
                collection_name=settings.qdrant_collection_name,
                points_selector=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_id",
                            match=models.MatchValue(value=request.file_id),
                        )
                    ]
                ),
            )
            status_msg = "updated"
            logger.info(f"Updated existing embeddings for file: {request.file_id}")
        else:
            status_msg = "created"
            logger.info(f"Creating new embeddings for file: {request.file_id}")

        # Upsert the new embedding
        qdrant_client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=[point_data],
            wait=True,
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
async def delete_embedding(request: DeleteRequest):
    """
    Delete endpoint - removes embeddings for a file.
    """
    try:
        logger.info(f"Deleting embeddings for file: {request.file_id}")

        # Delete all points with the given file_id
        qdrant_client.delete(
            collection_name=settings.qdrant_collection_name,
            points_selector=models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_id", match=models.MatchValue(value=request.file_id)
                    )
                ]
            ),
        )

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

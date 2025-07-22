import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from config import settings
from constants import DEFAULT_QUERY_LIMIT, MAX_QUERY_LIMIT
from database import search_embeddings, delete_file_embeddings, upsert_file_embedding
from models import (
    QueryRequest,
    QueryResponse,
    UpsertRequest,
    UpsertResponse,
    DeleteRequest,
    DeleteResponse,
)
from services import (
    get_embedding,
    get_summary,
    read_file_content,
    truncate_for_log,
    truncate_vector_for_log,
)

logger = logging.getLogger(settings.app_name)

# Create router
router = APIRouter()

# Constants for route logging
MAX_RESPONSE_LOG_LENGTH = 10  # Max number of results to log in detail


@router.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {
        "message": "Indexing Server is running",
        "version": settings.api_version,
        "status": "healthy",
    }


@router.post("/query", response_model=List[QueryResponse], tags=["Search"])
async def query_embeddings(request: QueryRequest):
    """
    Vector search endpoint with threshold filtering - returns array of file IDs and paths.
    Only returns results with similarity scores above the configured threshold.
    """
    try:
        logger.info(f"Processing search query: {truncate_for_log(request.text, 100)}")
        logger.debug(
            f"Query parameters - text: '{request.text}', limit: {request.limit}"
        )

        # Validate and set limit
        limit = request.limit or DEFAULT_QUERY_LIMIT
        if limit > MAX_QUERY_LIMIT:
            limit = MAX_QUERY_LIMIT
            logger.info(f"Query limit capped at {MAX_QUERY_LIMIT}")

        # Get embedding for the query text
        logger.debug("Getting embedding for query text")
        query_embedding = await get_embedding(request.text)
        logger.debug(
            f"Query embedding generated: {truncate_vector_for_log(query_embedding)}"
        )

        # Search the database with threshold filtering
        logger.debug(f"Searching database with threshold {settings.query_threshold}")
        results = search_embeddings(query_embedding, limit, settings.query_threshold)

        if not results:
            logger.info("No results found above threshold")
            return []

        # Convert results to response format
        response = [
            QueryResponse(
                file_id=result["file_id"],
                file_path=result["file_path"],
                score=float(result["score"]),
            )
            for result in results
        ]

        # Log results summary
        logger.info(
            f"Found {len(response)} results above threshold {settings.query_threshold}"
        )

        # Log first few results in detail
        log_count = min(len(response), MAX_RESPONSE_LOG_LENGTH)
        for i, result in enumerate(response[:log_count]):
            logger.debug(
                f"Result {i+1}: {result.file_id} - {truncate_for_log(result.file_path, 50)} (score: {result.score:.3f})"
            )

        if len(response) > MAX_RESPONSE_LOG_LENGTH:
            logger.debug(
                f"... and {len(response) - MAX_RESPONSE_LOG_LENGTH} more results"
            )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Query endpoint error: {e}")
        logger.error(f"Failed query text: {truncate_for_log(request.text)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.post("/upsert", response_model=UpsertResponse, tags=["Indexing"])
@router.put("/upsert", response_model=UpsertResponse, tags=["Indexing"])
async def upsert_embedding_endpoint(request: UpsertRequest):
    """
    Upsert endpoint - creates or updates embeddings for a file.
    Automatically reads file content from file_path, validates file type,
    and generates summary with proper text extraction.
    """
    try:
        logger.info(f"Processing upsert for file: {request.file_id}")
        logger.debug(f"File path: {request.file_path}")

        # Read and extract file content with type validation
        logger.debug("Reading and extracting file content")
        file_content = await read_file_content(request.file_path)
        logger.info(
            f"Extracted {len(file_content)} characters from file: {truncate_for_log(request.file_path, 60)}"
        )
        logger.debug(f"File content preview: {truncate_for_log(file_content, 200)}")

        # Generate summary from file content using improved prompting
        logger.debug("Generating summary from file content")
        summary = await get_summary(file_content, request.file_path)
        logger.info(f"Generated summary ({len(summary)} chars) for {request.file_id}")
        logger.debug(f"Summary content: {truncate_for_log(summary, 200)}")

        # Generate embedding from summary
        logger.debug("Generating embedding from summary")
        embedding = await get_embedding(summary)
        logger.info(
            f"Generated embedding vector for {request.file_id}: {truncate_vector_for_log(embedding)}"
        )

        # Upsert the file embedding using database function
        logger.debug("Upserting file embedding to database")
        status_msg = upsert_file_embedding(
            file_id=request.file_id,
            file_path=request.file_path,
            embedding=embedding,
            summary=summary,
        )

        logger.info(f"Successfully {status_msg} embedding for file: {request.file_id}")
        return UpsertResponse(
            message=f"File embedding {status_msg} successfully",
            file_id=request.file_id,
            status=status_msg,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise
    except Exception as e:
        logger.error(f"Upsert error for file {request.file_id}: {e}")
        logger.error(f"Failed file path: {truncate_for_log(request.file_path)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upsert failed: {str(e)}",
        )


@router.delete("/delete", response_model=DeleteResponse, tags=["Indexing"])
async def delete_embedding_endpoint(request: DeleteRequest):
    """
    Delete endpoint - removes embeddings for a file.
    Only requires file_id to identify and delete the file embeddings.
    """
    try:
        logger.info(f"Deleting embeddings for file: {request.file_id}")
        logger.debug("Starting deletion process from database")

        # Delete all points with the given file_id using database function
        delete_file_embeddings(request.file_id)

        logger.info(f"Successfully deleted embeddings for file: {request.file_id}")
        return DeleteResponse(
            message="File embeddings deleted successfully",
            file_id=request.file_id,
            status="deleted",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Delete error for file {request.file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}",
        )

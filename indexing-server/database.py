import logging
from typing import List, Optional, Tuple
from qdrant_client import QdrantClient, models
from qdrant_client.http import exceptions as qdrant_exceptions

from config import settings

logger = logging.getLogger(settings.app_name)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    host=settings.qdrant_host, port=settings.qdrant_port, check_compatibility=False
)


async def ensure_collection_exists():
    """Ensure the Qdrant collection exists with proper configuration."""
    try:
        qdrant_client.get_collection(collection_name=settings.qdrant_collection_name)
        logger.info(f"Collection '{settings.qdrant_collection_name}' exists")
    except qdrant_exceptions.UnexpectedResponse:
        # Collection doesn't exist, create it
        distance_metric = getattr(models.Distance, settings.distance_metric)
        qdrant_client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=models.VectorParams(
                size=settings.embedding_dimension,
                distance=distance_metric,
            ),
        )
        logger.info(f"Created collection '{settings.qdrant_collection_name}'")


def search_embeddings(
    query_vector: List[float], limit: int = 10, threshold: float = 0.0
) -> List[dict]:
    """
    Search for similar embeddings in the collection with threshold filtering.

    Args:
        query_vector: The embedding vector to search for
        limit: Maximum number of results to return
        threshold: Minimum similarity score threshold (0.0-1.0)

    Returns:
        List of dictionaries with file_id, file_path, and score
        Only returns results with scores >= threshold
    """
    try:
        logger.debug(f"Searching with limit={limit}, threshold={threshold}")

        results = qdrant_client.search(
            collection_name=settings.qdrant_collection_name,
            query_vector=query_vector,
            limit=limit,
        )

        logger.debug(f"Vector search returned {len(results)} raw results")

        # Filter by threshold and convert to dict format
        filtered_results = []
        for result in results:
            if result.score >= threshold:
                filtered_results.append(
                    {
                        "file_id": result.payload["file_id"],
                        "file_path": result.payload["file_path"],
                        "score": result.score,
                    }
                )

        logger.debug(f"After threshold filtering: {len(filtered_results)} results")
        return filtered_results

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise


def check_file_exists(file_id: str) -> bool:
    """
    Check if a file already has embeddings in the collection.

    Args:
        file_id: The unique identifier for the file

    Returns:
        True if file exists, False otherwise
    """
    try:
        existing_points, _ = qdrant_client.scroll(
            collection_name=settings.qdrant_collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_id", match=models.MatchValue(value=file_id)
                    )
                ]
            ),
            limit=1,
            with_payload=True,
        )
        exists = len(existing_points) > 0
        logger.debug(f"File {file_id} exists in collection: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Failed to check if file exists: {e}")
        raise


def delete_file_embeddings(file_id: str) -> None:
    """
    Delete all embeddings for a specific file from the collection.

    Args:
        file_id: The unique identifier for the file to delete
    """
    try:
        qdrant_client.delete(
            collection_name=settings.qdrant_collection_name,
            points_selector=models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_id", match=models.MatchValue(value=file_id)
                    )
                ]
            ),
        )
        logger.debug(f"Deleted embeddings for file: {file_id}")
    except Exception as e:
        logger.error(f"Failed to delete embeddings for file {file_id}: {e}")
        raise


def upsert_embedding(point_data: models.PointStruct) -> None:
    """
    Insert or update an embedding point in the collection.

    Args:
        point_data: The point structure containing vector and metadata
    """
    try:
        qdrant_client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=[point_data],
            wait=True,
        )
        logger.debug(f"Upserted embedding point with ID: {point_data.id}")
    except Exception as e:
        logger.error(f"Failed to upsert embedding: {e}")
        raise


def get_file_embeddings(file_id: str, limit: int = 100) -> List[models.Record]:
    """
    Retrieve all embedding points for a specific file.

    Args:
        file_id: The unique identifier for the file
        limit: Maximum number of points to retrieve

    Returns:
        List of records containing the embeddings and metadata
    """
    try:
        points, _ = qdrant_client.scroll(
            collection_name=settings.qdrant_collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_id", match=models.MatchValue(value=file_id)
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=True,
        )
        logger.debug(f"Retrieved {len(points)} embedding points for file: {file_id}")
        return points
    except Exception as e:
        logger.error(f"Failed to retrieve embeddings for file {file_id}: {e}")
        raise


def create_embedding_point(
    file_id: str,
    file_path: str,
    embedding: List[float],
    summary: str,
    point_id: Optional[str] = None,
) -> models.PointStruct:
    """
    Create a point structure for embedding data.

    Args:
        file_id: The unique identifier for the file
        file_path: The path to the file
        embedding: The embedding vector
        summary: The text summary/content
        point_id: Optional point ID, generates UUID if not provided

    Returns:
        A PointStruct ready for upserting to Qdrant
    """
    import uuid
    from datetime import datetime

    if point_id is None:
        point_id = str(uuid.uuid4())

    return models.PointStruct(
        id=point_id,
        vector=embedding,
        payload={
            "file_id": file_id,
            "file_path": file_path,
            "summary": summary,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        },
    )


def upsert_file_embedding(
    file_id: str, file_path: str, embedding: List[float], summary: str
) -> str:
    """
    Create and upsert an embedding for a file. Handles the complete workflow
    including checking for existing embeddings and replacing them if found.

    Args:
        file_id: The unique identifier for the file
        file_path: The path to the file
        embedding: The embedding vector
        summary: The text summary/content

    Returns:
        Status message indicating whether the file was "created" or "updated"
    """
    try:
        # Check if file already exists
        file_exists = check_file_exists(file_id)

        # If exists, delete old embeddings first
        if file_exists:
            delete_file_embeddings(file_id)
            status_msg = "updated"
            logger.info(f"Updated existing embeddings for file: {file_id}")
        else:
            status_msg = "created"
            logger.info(f"Creating new embeddings for file: {file_id}")

        # Create and upsert the new embedding
        point_data = create_embedding_point(file_id, file_path, embedding, summary)
        upsert_embedding(point_data)

        return status_msg
    except Exception as e:
        logger.error(f"Failed to upsert file embedding for {file_id}: {e}")
        raise

import logging
from qdrant_client import QdrantClient, models
from qdrant_client.http import exceptions as qdrant_exceptions

from config import settings

logger = logging.getLogger(settings.app_name)

# Initialize Qdrant client
qdrant_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


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

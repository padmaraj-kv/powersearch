from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """
    Configuration settings for the indexing server.

    Create a .env file in the same directory with these variables:

    # Server Configuration
    SERVER_HOST=0.0.0.0
    SERVER_PORT=5000
    SERVER_RELOAD=true

    # Qdrant Database Configuration
    QDRANT_HOST=localhost
    QDRANT_PORT=6333
    QDRANT_COLLECTION_NAME=file_embeddings

    # Ollama Configuration
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_SUMMARY_MODEL=gemma3:4b
    OLLAMA_EMBEDDING_MODEL=nomic-embed-text

    # Vector Configuration
    EMBEDDING_DIMENSION=768
    DISTANCE_METRIC=COSINE

    # Query Configuration
    QUERY_THRESHOLD=0.4

    # API Configuration
    API_TITLE=Indexing Server
    API_DESCRIPTION=FastAPI server for file indexing with vector embeddings
    API_VERSION=1.0.0

    # Logging Configuration
    LOG_LEVEL=INFO
    APP_NAME=indexing-server
    """

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 5000
    server_reload: bool = True

    # Qdrant Database Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "file_embeddings"

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_summary_model: str = "gemma3:4b"
    ollama_embedding_model: str = "nomic-embed-text"

    # Vector Configuration
    embedding_dimension: int = 768
    distance_metric: Literal["COSINE", "EUCLIDEAN", "DOT"] = "COSINE"

    # Query Configuration
    query_threshold: float = 0.4

    # API Configuration
    api_title: str = "Indexing Server"
    api_description: str = "FastAPI server for file indexing with vector embeddings"
    api_version: str = "1.0.0"

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    app_name: str = "indexing-server"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

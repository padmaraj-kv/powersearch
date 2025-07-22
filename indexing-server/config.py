from pydantic_settings import BaseSettings
from typing import Literal, Optional
from pydantic import validator


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

    # Ollama Configuration (Local Models)
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_SUMMARY_MODEL=gemma3:4b
    OLLAMA_VISION_MODEL=qwen2.5-vl:7b
    OLLAMA_EMBEDDING_MODEL=nomic-embed-text

    # Online Model Configuration
    USE_ONLINE_MODELS=false
    ONLINE_SUMMARY_MODEL=gemini/gemini-1.5-flash
    ONLINE_VISION_MODEL=gemini/gemini-1.5-flash
    GEMINI_API_KEY=your_gemini_api_key_here

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

    # Ollama Configuration (Local Models)
    ollama_base_url: str = "http://localhost:11434"
    ollama_summary_model: str = "gemma3:4b"
    ollama_vision_model: str = "qwen2.5-vl:7b"
    ollama_embedding_model: str = "nomic-embed-text"

    # Online Model Configuration
    use_online_models: bool = False
    online_summary_model: str = "gemini/gemini-1.5-flash"
    online_vision_model: str = "gemini/gemini-1.5-flash"
    gemini_api_key: Optional[str] = None

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

    @validator("gemini_api_key", always=True)
    def validate_gemini_api_key(cls, v, values):
        """Validate Gemini API key is provided when online models are enabled."""
        use_online = values.get("use_online_models", False)
        if use_online and not v:
            raise ValueError(
                "GEMINI_API_KEY is required when USE_ONLINE_MODELS=true. "
                "Please set your Gemini API key in the .env file."
            )
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

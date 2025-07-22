# Indexing Server

A FastAPI-based indexing server that provides vector embeddings and search capabilities using Qdrant and Ollama for file content indexing.

## Features

- **Vector Search**: Query files by semantic similarity using vector embeddings
- **File Indexing**: Upsert file content with automatic summarization and embedding generation
- **File Management**: Delete file embeddings from the vector database
- **Local AI Models**: Uses Ollama for text summarization and embedding generation
- **Configurable**: Environment-based configuration using Pydantic settings
- **Comprehensive Logging**: Configurable log levels and structured logging

## Prerequisites

- Python 3.12+
- Poetry for dependency management
- Qdrant vector database
- Ollama with required models:
  - `gemma2:2b` (for text summarization)
  - `nomic-embed-text` (for embeddings)

## Installation

1. Install dependencies using Poetry:

```bash
poetry install
```

2. Create a `.env` file based on the configuration template (see Configuration section).

3. Ensure Qdrant is running:

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant
```

4. Ensure Ollama is running with required models:

```bash
# Pull required models
ollama pull gemma2:2b
ollama pull nomic-embed-text
```

## Configuration

Create a `.env` file in the indexing-server directory with the following variables:

```env
# Server Configuration
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
SERVER_RELOAD=true

# Qdrant Database Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=file_embeddings

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_SUMMARY_MODEL=gemma2:2b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Vector Configuration
EMBEDDING_DIMENSION=768
DISTANCE_METRIC=COSINE

# API Configuration
API_TITLE=Indexing Server
API_DESCRIPTION=FastAPI server for file indexing with vector embeddings
API_VERSION=1.0.0

# Logging Configuration
LOG_LEVEL=INFO
APP_NAME=indexing-server
```

## Running the Server

Start the server using Poetry:

```bash
poetry run python3 app.py
```

The server will start on `http://localhost:5000` by default.

## API Endpoints

### Health Check

```http
GET /
```

Returns server status and version information.

### Query (Vector Search)

```http
POST /query
```

**Request Body:**

```json
{
  "text": "search query text",
  "limit": 10
}
```

**Response:**

```json
[
  {
    "file_id": "unique-file-id",
    "file_path": "/path/to/file.txt",
    "score": 0.85
  }
]
```

### Upsert (Create/Update Embeddings)

```http
POST /upsert
PUT /upsert
```

**Request Body:**

```json
{
  "file_id": "unique-file-id",
  "file_path": "/path/to/file.txt"
}
```

**Response:**

```json
{
  "message": "File embedding created successfully",
  "file_id": "unique-file-id",
  "status": "created"
}
```

**Note:** The server automatically reads the file content from `file_path`, generates a summary using the configured AI model, and creates embeddings. The file must be accessible from the server's file system.

### Delete Embeddings

```http
DELETE /delete
```

**Request Body:**

```json
{
  "file_id": "unique-file-id",
  "file_path": "/path/to/file.txt"
}
```

**Response:**

```json
{
  "message": "File embeddings deleted successfully",
  "file_id": "unique-file-id",
  "status": "deleted"
}
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## Architecture

The server uses:

- **FastAPI** for the REST API framework
- **Qdrant** as the vector database for storing embeddings
- **Ollama** for local AI model inference (summaries and embeddings)
- **Pydantic Settings** for configuration management
- **httpx** for async HTTP requests to Ollama

## Data Flow

1. **Upsert**: File path → Read file content → Summarization (Ollama) → Embedding generation (Ollama) → Storage (Qdrant)
2. **Query**: Query text → Embedding generation (Ollama) → Vector search (Qdrant) → Results
3. **Delete**: File ID → Remove embeddings (Qdrant)

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

- `200`: Success
- `201`: Created (for upsert operations)
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error (processing failures)
- `503`: Service Unavailable (external service failures)

## Development

### Project Structure

```
indexing-server/
├── app.py              # FastAPI application entry point
├── config.py           # Configuration settings with Pydantic
├── models.py           # Pydantic data models for requests/responses
├── database.py         # Qdrant client and database operations
├── services.py         # Ollama service functions (embedding, summary)
├── routes.py           # API route definitions and handlers
├── pyproject.toml      # Poetry dependencies and project metadata
├── docker-compose.yml  # Qdrant service setup
├── .env               # Environment variables (create this)
└── README.md          # This file
```

### Adding Dependencies

Use Poetry to add new dependencies:

```bash
poetry add <package-name>
```

### Running in Development Mode

The server runs with hot-reload enabled by default when `SERVER_RELOAD=true` is set in the `.env` file.

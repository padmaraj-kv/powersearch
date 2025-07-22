# PowerSearch

A comprehensive search and indexing system with vector embeddings and semantic search capabilities.

## Project Structure

### Indexing Server (`/indexing-server`)

FastAPI-based indexing server that provides vector embeddings and search capabilities using Qdrant and Ollama for file content indexing.

**Features:**

- Vector search with semantic similarity
- File content indexing with automatic summarization
- Local AI models via Ollama integration
- RESTful API with automatic documentation

**Technologies:** FastAPI, Qdrant, Ollama, Pydantic

**Key Endpoints:**

- `POST /query` - Semantic search
- `POST/PUT /upsert` - Index file content
- `DELETE /delete` - Remove file embeddings

See [indexing-server/README.md](indexing-server/README.md) for detailed setup and usage instructions.

### Other Components

- `file-server/` - File serving functionality
- `frontend/` - User interface components

## Getting Started

Each component has its own setup instructions. Start with the indexing server for core search functionality:

```bash
cd indexing-server
poetry install
# Create .env file (see indexing-server/README.md)
poetry run python3 app.py
```

## Development

This project uses Poetry for Python dependency management and follows industry-standard practices for each component.

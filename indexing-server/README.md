# Indexing Server

A FastAPI-based indexing server that provides vector embeddings and search capabilities using Qdrant and Ollama for file content indexing. The server now supports multiple file types, includes PDF text extraction, threshold-based filtering, and improved AI integration through LiteLLM.

## Features

- **Multi-format File Support**: Index text files, PDFs, DOCX, code files, configuration files, and more
- **PDF Text Extraction**: Automatic text extraction from PDF documents using PyPDF2
- **DOCX Support**: Extract text from Microsoft Word documents
- **Vision Support**: Process images and visual content using Gemma3's multimodal capabilities
- **Vector Search**: Query files by semantic similarity using vector embeddings with threshold filtering
- **File Indexing**: Upsert file content with automatic summarization and embedding generation
- **File Management**: Delete file embeddings from the vector database
- **Local AI Models**: Uses Ollama via LiteLLM for text summarization and embedding generation
- **Network Access**: Server exposed to network for remote access from other machines
- **Intelligent Chunking**: Handle large files by processing them in chunks with comprehensive summarization
- **File Type Validation**: Automatic validation of supported file types with graceful error handling
- **Configurable Thresholds**: Filter search results based on similarity score thresholds
- **Comprehensive Logging**: Configurable log levels and structured logging

## Supported File Types

### Text Files

- `.txt`, `.md`, `.py`, `.js`, `.ts`, `.jsx`, `.tsx`
- `.html`, `.htm`, `.css`, `.json`, `.xml`
- `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`
- `.sh`, `.bat`, `.ps1`, `.sql`, `.csv`, `.log`

### Code Files

- `.c`, `.cpp`, `.h`, `.hpp`, `.java`, `.go`, `.rs`
- `.php`, `.rb`, `.swift`, `.kt`, `.scala`, `.r`, `.m`

### Document Files

- `.pdf` (with text extraction)
- `.docx` (Microsoft Word)
- `.rtf`, `.doc`

## Prerequisites

- Python 3.12+
- Poetry for dependency management
- Qdrant vector database
- Ollama with required models:
  - `gemma3:4b` (for text summarization and vision processing)
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
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

## Configuration

Create a `.env` file in the indexing-server directory with the following variables:

```env
# Server Configuration - Network Access
SERVER_HOST=0.0.0.0    # Expose to all network interfaces (use 127.0.0.1 for localhost only)
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
```

## Running the Server

### Option 1: Direct Python Execution

Start the server using Poetry:

```bash
poetry run python3 app.py
```

The server will start on `http://0.0.0.0:5000` by default, making it accessible from other machines on the network.

### Option 2: Docker Compose (Recommended)

For a complete deployment with Qdrant:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Network Access

The server is configured to accept connections from any network interface (`0.0.0.0`). You can access it from:

- **Local machine**: `http://localhost:5000`
- **Same network**: `http://<server-ip>:5000` (replace `<server-ip>` with the actual IP address)
- **Docker internal**: `http://indexing-server:5000` (from other containers)

### Finding Your Server IP

```bash
# Linux/macOS
ip addr show | grep inet
# or
ifconfig | grep inet

# Windows
ipconfig
```

### Security Considerations

- The server is exposed to the network without authentication by default
- For production use, consider:
  - Adding authentication/API keys
  - Using HTTPS/TLS
  - Firewall rules to restrict access
  - Running behind a reverse proxy (nginx, traefik)

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

**Note:** Only returns results with similarity scores above the configured threshold (default: 0.4).

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

**Enhanced Features:**

- Automatic file type validation
- PDF text extraction
- DOCX text extraction
- Image processing with Gemma3 vision capabilities
- Intelligent text chunking for large files
- Improved summarization with context-aware prompts
- File size validation (10MB limit)

### Delete Embeddings

```http
DELETE /delete
```

**Request Body:**

```json
{
  "file_id": "unique-file-id"
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

- Swagger UI: `http://<server-ip>:5000/docs`
- ReDoc: `http://<server-ip>:5000/redoc`

## Architecture

The server uses:

- **FastAPI** for the REST API framework
- **Qdrant** as the vector database for storing embeddings
- **Ollama** via **LiteLLM** for local AI model inference (summaries and embeddings)
- **Gemma3 4B** for text summarization and vision processing
- **PyPDF2** for PDF text extraction
- **python-docx** for DOCX document processing
- **Pydantic Settings** for configuration management
- **Structured Prompts** for improved AI interactions

## Data Flow

1. **Upsert**: File path → File type validation → Text/Image extraction (PDF/DOCX/images) → Chunking (if needed) → Summarization (Gemma3 via LiteLLM) → Embedding generation → Storage (Qdrant)
2. **Query**: Query text → Embedding generation → Vector search → Threshold filtering → Results
3. **Delete**: File ID → Remove embeddings (Qdrant)

## File Processing

### PDF Files

- Extracts text from all pages
- Handles encrypted PDFs gracefully
- Skips pages that cannot be processed

### DOCX Files

- Extracts text from all paragraphs
- Preserves document structure
- Handles complex document formatting

### Large Files

- Automatically chunks files larger than 50,000 characters
- Creates summaries for each chunk
- Generates comprehensive final summary from chunk summaries

### Text Files

- Supports multiple encodings (UTF-8, Latin-1, CP1252)
- Graceful fallback for encoding issues
- Preserves file structure

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

- `200`: Success
- `201`: Created (for upsert operations)
- `400`: Bad Request (invalid input)
- `404`: Not Found (file doesn't exist)
- `413`: Payload Too Large (file size exceeded)
- `422`: Unprocessable Entity (unsupported file type, invalid content)
- `500`: Internal Server Error (processing failures)
- `503`: Service Unavailable (external service failures)

## Development

### Project Structure

```
indexing-server/
├── app.py              # FastAPI application entry point
├── config.py           # Configuration settings with Pydantic
├── constants.py        # Constants for file types, limits, etc.
├── prompts.py          # AI prompts for summarization
├── models.py           # Pydantic data models for requests/responses
├── database.py         # Qdrant client and database operations
├── services.py         # File processing and AI service functions
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

### Key Improvements

1. **Better File Support**: Added support for PDFs, DOCX, and numerous code/config file types
2. **Improved AI Integration**: Using LiteLLM for better Ollama integration with proper async support
3. **Enhanced Prompting**: Structured prompts in `prompts.py` for better summarization quality
4. **File Validation**: Comprehensive file type and size validation
5. **Chunking Strategy**: Intelligent text chunking with sentence/paragraph boundary detection
6. **Threshold Filtering**: Configurable similarity score thresholds for query results
7. **Error Handling**: Graceful handling of various file processing errors

### Running in Development Mode

The server runs with hot-reload enabled by default when `SERVER_RELOAD=true` is set in the `.env` file.

## Configuration Options

- **Query Threshold**: Set minimum similarity score for search results (0.0-1.0)
- **File Size Limits**: Maximum file size for processing (default: 10MB)
- **Text Chunking**: Configurable chunk size for large file processing
- **Model Selection**: Choose different Ollama models for summarization and embeddings
- **Logging Levels**: Configurable logging with structured output

# Indexing Server

A FastAPI-based indexing server that provides vector embeddings and search capabilities using Qdrant and Ollama for file content indexing. The server now supports multiple file types, includes PDF text extraction, threshold-based filtering, improved AI integration through LiteLLM, and configurable online model support.

## Features

- **Multi-format File Support**: Index text files, PDFs, DOCX, code files, configuration files, and more
- **PDF Text Extraction**: Automatic text extraction from PDF documents using PyPDF2
- **DOCX Support**: Extract text from Microsoft Word documents
- **Advanced Vision Support**: Process images and visual content using specialized vision models
- **Flexible Model Configuration**: Choose between local (Ollama) and online models (Gemini)
- **Content-Focused Image Analysis**: Optimized prompts for extracting searchable content from images
- **Vector Search**: Query files by semantic similarity using vector embeddings with threshold filtering
- **File Indexing**: Upsert file content with automatic summarization and embedding generation
- **File Management**: Delete file embeddings from the vector database
- **Robust Error Handling**: Prevents embedding generation if content extraction or summarization fails
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

### Image Files

- `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`
- Uses specialized vision models for content extraction

## Prerequisites

### Local Models (Ollama)

- Python 3.12+
- Poetry for dependency management
- Qdrant vector database
- Ollama with required models:
  - `gemma3:4b` (for text summarization)
  - `qwen2.5-vl:7b` (for vision processing)
  - `nomic-embed-text` (for embeddings)

### Online Models (Optional)

- Valid API keys for online services (e.g., Google AI API for Gemini)
- Environment variables configured for API access

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

4. For local models, ensure Ollama is running with required models:

```bash
# Pull required models
ollama pull gemma3:4b
ollama pull qwen2.5-vl:7b
ollama pull nomic-embed-text
```

## Configuration

Create a `.env` file in the indexing-server directory with the following variables:

### Complete .env Configuration Template

```env
# ===== SERVER CONFIGURATION =====
# Network access configuration
SERVER_HOST=0.0.0.0               # Expose to all network interfaces (use 127.0.0.1 for localhost only)
SERVER_PORT=5000                  # Port for the FastAPI server
SERVER_RELOAD=true                # Enable hot-reload in development

# ===== QDRANT DATABASE CONFIGURATION =====
# Vector database settings
QDRANT_HOST=localhost             # Qdrant server host
QDRANT_PORT=6333                  # Qdrant server port
QDRANT_COLLECTION_NAME=file_embeddings  # Collection name for storing embeddings

# ===== OLLAMA CONFIGURATION (LOCAL MODELS) =====
# Local AI model settings via Ollama
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server URL
OLLAMA_SUMMARY_MODEL=gemma3:4b           # Model for text summarization
OLLAMA_VISION_MODEL=qwen2.5-vl:7b       # Model for image vision processing
OLLAMA_EMBEDDING_MODEL=nomic-embed-text  # Model for vector embeddings

# ===== ONLINE MODEL CONFIGURATION =====
# Cloud-based AI model settings (optional)
USE_ONLINE_MODELS=false                     # Enable/disable online models
ONLINE_SUMMARY_MODEL=gemini/gemini-1.5-flash  # Online model for text summarization
ONLINE_VISION_MODEL=gemini/gemini-1.5-flash   # Online model for image processing
GEMINI_API_KEY=your_gemini_api_key_here       # Required only if USE_ONLINE_MODELS=true

# ===== VECTOR CONFIGURATION =====
# Embedding and vector search settings
EMBEDDING_DIMENSION=768           # Dimension of embedding vectors
DISTANCE_METRIC=COSINE           # Distance metric (COSINE, EUCLIDEAN, DOT)

# ===== QUERY CONFIGURATION =====
# Search behavior settings
QUERY_THRESHOLD=0.4              # Minimum similarity score for search results (0.0-1.0)

# ===== API CONFIGURATION =====
# FastAPI server metadata
API_TITLE=Indexing Server
API_DESCRIPTION=FastAPI server for file indexing with vector embeddings
API_VERSION=1.0.0

# ===== LOGGING CONFIGURATION =====
# Application logging settings
LOG_LEVEL=INFO                   # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
APP_NAME=indexing-server         # Application name for logging
```

### Model Configuration Options

#### Option 1: Local Models Only (Default)

For completely local processing using Ollama:

```env
# Use local models
USE_ONLINE_MODELS=false

# Configure Ollama models
OLLAMA_SUMMARY_MODEL=gemma3:4b
OLLAMA_VISION_MODEL=qwen2.5-vl:7b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# No API key required
# GEMINI_API_KEY is optional when using local models
```

#### Option 2: Online Models (Gemini)

For cloud-based processing with better performance:

```env
# Enable online models
USE_ONLINE_MODELS=true

# Configure online models
ONLINE_SUMMARY_MODEL=gemini/gemini-1.5-flash
ONLINE_VISION_MODEL=gemini/gemini-1.5-flash

# Required: Set your Gemini API key
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

#### Option 3: Hybrid Configuration

You can easily switch between local and online models by changing just one setting:

```env
# Toggle between local and online models
USE_ONLINE_MODELS=false  # Set to true to use online models

# Both configurations available
OLLAMA_SUMMARY_MODEL=gemma3:4b
OLLAMA_VISION_MODEL=qwen2.5-vl:7b
ONLINE_SUMMARY_MODEL=gemini/gemini-1.5-flash
ONLINE_VISION_MODEL=gemini/gemini-1.5-flash

# API key only validated when USE_ONLINE_MODELS=true
GEMINI_API_KEY=your_api_key_here
```

### API Key Management

- **Local Models**: No API key required
- **Online Models**: Requires `GEMINI_API_KEY` when `USE_ONLINE_MODELS=true`
- **Validation**: API key is only validated when online models are enabled
- **Security**: Keep your API key secure and don't commit it to version control

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and set it in your `.env` file

### Environment Variable Priority

The configuration system follows this priority order:

1. Environment variables (highest priority)
2. `.env` file values
3. Default values in code (lowest priority)

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
- Specialized image processing with content-focused prompts
- Intelligent text chunking for large files
- Improved summarization with context-aware prompts
- File size validation (10MB limit)
- **Robust error handling**: Stops processing if content extraction or summarization fails

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
- **LiteLLM** for unified AI model access (local and online)
- **Local Models** via **Ollama**: Gemma3 for text, Qwen2.5-VL for vision, Nomic-Embed for embeddings
- **Online Models**: Gemini (or other providers) via LiteLLM
- **PyPDF2** for PDF text extraction
- **python-docx** for DOCX document processing
- **Pillow** for image processing
- **Pydantic Settings** for configuration management
- **Specialized Prompts** for improved AI interactions

## Data Flow

1. **Upsert**: File path → File type validation → Text/Image extraction (PDF/DOCX/images) → Chunking (if needed) → Summarization (local/online) → Embedding generation → Storage (Qdrant)
2. **Query**: Query text → Embedding generation → Vector search → Threshold filtering → Results
3. **Delete**: File ID → Remove embeddings (Qdrant)

**Error Handling**: If content extraction or summarization fails, the process stops and no embedding is generated.

## File Processing

### PDF Files

- Extracts text from all pages
- Handles encrypted PDFs gracefully
- Skips pages that cannot be processed

### DOCX Files

- Extracts text from all paragraphs
- Preserves document structure
- Handles complex document formatting

### Image Files

- **Advanced vision processing** with specialized models
- **Content-focused extraction** optimized for search
- Extracts text, objects, UI elements, and contextual information
- Uses `qwen2.5-vl:7b` locally or Gemini online
- **Fails fast**: Raises error if vision processing fails

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
- `422`: Unprocessable Entity (unsupported file type, invalid content, vision processing failed)
- `500`: Internal Server Error (processing failures)
- `503`: Service Unavailable (external service failures, LLM failures)

**Key Improvements**:

- **Fail-fast approach**: Processing stops immediately if any step fails
- **No partial processing**: Embeddings are only generated after successful content extraction and summarization
- **Clear error messages**: Detailed feedback on what went wrong

## Development

### Project Structure

```
indexing-server/
├── app.py              # FastAPI application entry point
├── config.py           # Configuration settings with model selection
├── constants.py        # Constants for file types, limits, etc.
├── prompts.py          # AI prompts for summarization and image analysis
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

1. **Flexible Model Configuration**: Switch between local and online models with a single config
2. **Specialized Vision Processing**: Uses `qwen2.5-vl:7b` for better image content extraction
3. **Content-Focused Prompts**: Optimized prompts for extracting searchable content from images
4. **Robust Error Handling**: Prevents embedding generation if LLM calls fail
5. **Online Model Support**: Seamless integration with Gemini and other online providers
6. **Better Logging**: Clear information about which models are being used
7. **Fail-Fast Processing**: Stops immediately on errors to prevent partial/corrupted data

### Running in Development Mode

The server runs with hot-reload enabled by default when `SERVER_RELOAD=true` is set in the `.env` file.

## Configuration Options

- **Model Selection**: Choose between local Ollama models and online providers
- **Vision Models**: Separate configuration for vision processing (`qwen2.5-vl:7b` or Gemini)
- **Query Threshold**: Set minimum similarity score for search results (0.0-1.0)
- **File Size Limits**: Maximum file size for processing (default: 10MB)
- **Text Chunking**: Configurable chunk size for large file processing
- **Logging Levels**: Configurable logging with structured output

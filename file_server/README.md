# File Server

A real-time file monitoring and indexing system that watches a directory for file system changes and provides a web API for file search functionality.

## Overview

The File Server consists of two main components:

1. **File Monitor** (`main.py`) - Monitors file system events and maintains a database of file records
2. **Web Server** (`server.py`) - Provides REST API endpoints for file search and health checks

## Architecture

```
File System Changes → File Monitor → Database → Indexing Server
                                        ↓
                      Web Server ← API Requests
```

### Core Components

- **File Monitor**: Uses the `watchdog` library to detect file system events (create, modify, delete, move)
- **Database Layer**: Stores file metadata and tracks file states
- **Indexing Integration**: Communicates with an external indexing server (port 5001) for search functionality
- **Web API**: FastAPI server that provides search endpoints

## Programs

### 1. File Monitor (`main.py`)

The file monitoring program that watches for file system changes in a configured directory.

**Features:**
- Real-time file system event detection
- Automatic database record management
- Integration with external indexing server
- Support for file creation, modification, deletion, and move operations

**Usage:**
```bash
python main.py
```

**What it does:**
- Monitors the configured directory (`~/Desktop/personal/listen_here` by default)
- Detects file system events (create, modify, delete, move)
- Updates local database with file records
- Pushes file data to indexing server for search functionality

### 2. Web Server (`server.py`)

A FastAPI-based web server that provides REST API endpoints for file operations.

**Usage:**
```bash
python server.py
```

**Endpoints:**
- `GET /` - Root endpoint with server information
- `GET /health` - Health check endpoint
- `GET /files?search=<query>` - Search files using the query parameter

**Server Details:**
- Runs on `0.0.0.0:4000`
- Integrates with the indexing server for search functionality
- Returns file paths matching search queries

## Setup and Installation

### Prerequisites

1. Python 3.7+
2. PostgreSQL database (configured in the database layer)
3. External indexing server running on `localhost:5001`

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the monitoring directory in `file_monitor/config.py`:
```python
ROOT_DIR = Path.home() / "your/desired/directory"
```

3. Set up database connection (configure in `file_monitor/db.py`)

4. Ensure the indexing server is running on `localhost:5001`

## Dependencies

- `psycopg2-binary` - PostgreSQL database adapter
- `python-dotenv` - Environment variable management
- `pypika` - SQL query builder
- `pydantic` - Data validation
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `watchdog` - File system monitoring

## Configuration

### Monitoring Directory

Edit `file_monitor/config.py` to change the monitored directory:

```python
ROOT_DIR = Path.home() / "your/target/directory"
```

### Database Configuration

Configure database connection in `file_monitor/db.py` and related database setup.

### Indexing Server Integration

The system expects an indexing server running on `localhost:5001` with the following endpoints:
- `POST /upsert` - For adding/updating file records
- `POST /query` - For searching files
- `DELETE /delete` - for removing file records

## File System Events Handled

- **Created**: New files and directories
- **Modified**: File content changes
- **Deleted**: File and directory removals
- **Moved**: File and directory renames/moves

## Database Schema

The system maintains file records with:
- Unique file ID
- File path
- Deletion status
- Creation and update timestamps

## Usage Examples

### Starting the File Monitor

```bash
cd file_server
python main.py
```

Output:
```
Starting file monitor on: /Users/username/Desktop/personal/listen_here
Press Ctrl+C to stop monitoring...
```

### Starting the Web Server

```bash
cd file_server
python server.py
```

### Searching Files

```bash
curl "http://localhost:4000/files?search=my_document"
```

Response:
```json
{
  "files": [
    "/path/to/my_document.txt",
    "/path/to/another_my_document.pdf"
  ]
}
```

### Health Check

```bash
curl http://localhost:4000/health
```

Response:
```json
{
  "status": "healthy",
  "message": "Server is running"
}
```

## Development

### Running Both Programs

For full functionality, run both programs simultaneously:

1. Terminal 1 - Start file monitor:
```bash
python main.py
```

2. Terminal 2 - Start web server:
```bash
python server.py
```

### Testing

A test file `test_inde_server.py` is included for testing the indexing server integration.

## Troubleshooting

1. **Monitor not starting**: Ensure the configured `ROOT_DIR` exists
2. **Database errors**: Check PostgreSQL connection and database setup
3. **Indexing errors**: Verify the indexing server is running on `localhost:5001`
4. **No search results**: Ensure files have been properly indexed after modification

## Architecture Notes

- The system only processes file events (not directory events) for indexing
- File records are maintained locally and synchronized with the external indexing server
- The web server provides a thin API layer over the indexing functionality
- All file system events are logged for debugging purposes

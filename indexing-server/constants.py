# Supported file types for indexing
SUPPORTED_FILE_TYPES = {
    # Text files
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".py": "text/python",
    ".js": "text/javascript",
    ".ts": "text/typescript",
    ".jsx": "text/jsx",
    ".tsx": "text/tsx",
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".json": "application/json",
    ".xml": "text/xml",
    ".yaml": "text/yaml",
    ".yml": "text/yaml",
    ".toml": "text/toml",
    ".ini": "text/ini",
    ".cfg": "text/config",
    ".conf": "text/config",
    ".sh": "text/shell",
    ".bat": "text/batch",
    ".ps1": "text/powershell",
    ".sql": "text/sql",
    ".csv": "text/csv",
    ".log": "text/log",
    # Document files
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".rtf": "text/rtf",
    # Code files
    ".c": "text/c",
    ".cpp": "text/cpp",
    ".h": "text/c-header",
    ".hpp": "text/cpp-header",
    ".java": "text/java",
    ".go": "text/go",
    ".rs": "text/rust",
    ".php": "text/php",
    ".rb": "text/ruby",
    ".swift": "text/swift",
    ".kt": "text/kotlin",
    ".scala": "text/scala",
    ".r": "text/r",
    ".m": "text/matlab",
    # Image files (processed with vision)
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}

# Maximum file size for processing (in bytes) - 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Maximum text length for summarization (in characters)
MAX_TEXT_LENGTH = 50000

# Chunk size for large text processing
CHUNK_SIZE = 1000

# Default query limit
DEFAULT_QUERY_LIMIT = 10

# Maximum query limit
MAX_QUERY_LIMIT = 100

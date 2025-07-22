"""File event types enumeration for the file monitor system."""

from enum import Enum


class FileEventType(Enum):
    """Enumeration of file system event types."""
    
    CREATED = "created"
    MODIFIED = "modified" 
    DELETED = "deleted"
    MOVED = "moved" 
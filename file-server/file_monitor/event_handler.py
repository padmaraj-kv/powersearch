"""Central event handler for file system events."""

from .event_types import FileEventType
from .file_event_handlers import handle_modify, handle_move, handle_delete


def handle_event(event_type: FileEventType, data: dict) -> None:
    """
    Central handler function for all file system events.
    
    Args:
        event_type: The type of file system event that occurred
        data: Dictionary containing event-specific data (path, timestamps, etc.)
    """
    if data.get("is_directory") is False:
        if event_type == FileEventType.CREATED:
            return
        elif event_type == FileEventType.MODIFIED:
            handle_modify(data)
        elif event_type == FileEventType.MOVED:
            handle_move(data)
        elif event_type == FileEventType.DELETED:
            handle_delete(data) 
"""Central event handler for file system events."""

from .event_types import FileEventType


def handle_event(event_type: FileEventType, data: dict) -> None:
    """
    Central handler function for all file system events.
    
    Args:
        event_type: The type of file system event that occurred
        data: Dictionary containing event-specific data (path, timestamps, etc.)
    """
    # Only print if the event is about a file (not a directory)
    if data.get("is_directory") is False:
        # Suppress CREATED events for files
        if event_type == FileEventType.CREATED:
            return
        print(f"[FILE MONITOR] Event Type: {event_type.value.upper()}")
        print(f"[FILE MONITOR] Event Data:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print("-" * 50) 
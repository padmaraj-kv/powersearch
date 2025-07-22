"""Main file watcher implementation using watchdog library."""

import sys
import time
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import ROOT_DIR
from .event_types import FileEventType
from .event_handler import handle_event


def get_file_type(file_path: str) -> str:
    """Extract file type/extension from file path."""
    if Path(file_path).is_dir():
        return "directory"
    
    suffix = Path(file_path).suffix.lower()
    if suffix:
        return suffix[1:]  # Remove the dot from extension
    else:
        return "no_extension"


class FileMonitorHandler(FileSystemEventHandler):
    """File system event handler that processes all file system events."""
    
    def on_created(self, event):
        """Handle file/directory creation events."""
        data = {
            "path": event.src_path,
            "is_directory": event.is_directory,
            "file_type": get_file_type(event.src_path),
            "timestamp": datetime.now().isoformat(),
            "event_src": "filesystem"
        }
        handle_event(FileEventType.CREATED, data)
    
    def on_modified(self, event):
        """Handle file/directory modification events."""
        data = {
            "path": event.src_path,
            "is_directory": event.is_directory,
            "file_type": get_file_type(event.src_path),
            "timestamp": datetime.now().isoformat(),
            "event_src": "filesystem"
        }
        handle_event(FileEventType.MODIFIED, data)
    
    def on_deleted(self, event):
        """Handle file/directory deletion events."""
        data = {
            "path": event.src_path,
            "is_directory": event.is_directory,
            "file_type": get_file_type(event.src_path),
            "timestamp": datetime.now().isoformat(),
            "event_src": "filesystem"
        }
        handle_event(FileEventType.DELETED, data)
    
    def on_moved(self, event):
        """Handle file/directory move/rename events."""
        data = {
            "src_path": event.src_path,
            "dest_path": event.dest_path,
            "is_directory": event.is_directory,
            "src_file_type": get_file_type(event.src_path),
            "dest_file_type": get_file_type(event.dest_path),
            "timestamp": datetime.now().isoformat(),
            "event_src": "filesystem"
        }
        handle_event(FileEventType.MOVED, data)


def start_monitoring():
    """Start the file system monitor."""
    # Ensure the root directory exists
    if not ROOT_DIR.exists():
        print(f"Error: Root directory {ROOT_DIR} does not exist!")
        sys.exit(1)
    
    print(f"Starting file monitor on: {ROOT_DIR}")
    print("Press Ctrl+C to stop monitoring...")
    
    # Create event handler and observer
    event_handler = FileMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, str(ROOT_DIR), recursive=True)
    
    # Start monitoring
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping file monitor...")
        observer.stop()
    
    observer.join()
    print("File monitor stopped.")


if __name__ == "__main__":
    start_monitoring() 
"""File monitor package for watching file system changes."""

from .event_types import FileEventType
from .event_handler import handle_event
from .config import ROOT_DIR

__version__ = "1.0.0"
__all__ = ["FileEventType", "handle_event", "ROOT_DIR"] 
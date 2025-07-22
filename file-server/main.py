#!/usr/bin/env python3
"""
Main entry point for the file monitor application.

This demonstrates how to use the file_monitor package to watch for 
file system changes in the configured root directory.
"""

from file_monitor.watcher import start_monitoring

if __name__ == "__main__":
    start_monitoring() 
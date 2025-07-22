#!/usr/bin/env python3
"""
Simple FastAPI server with health endpoint.
"""

from fastapi import FastAPI
from file_monitor.push_to_index import push
import uvicorn

app = FastAPI(title="File Server", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Server is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "File Server is running", "health_endpoint": "/health"}

@app.get("/files")
async def search_files(search: str):
    """Search files endpoint"""
    print(f"[LOG] Searching for files with search: {search}")
    response = push({"path": search}, "search")
    
    # Extract file paths from the response
    if response and isinstance(response, list):
        file_paths = [item.get("file_path") for item in response if "file_path" in item]
        print(f"[LOG] Extracted {len(file_paths)} file paths from search response")
        return {"files": file_paths}
    else:
        print(f"[LOG] No valid response or empty response: {response}")
        return {"files": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)

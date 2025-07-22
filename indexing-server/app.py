import logging

from fastapi import FastAPI

from config import settings
from database import ensure_collection_exists
from routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=f"%(asctime)s - {settings.app_name} - %(levelname)s - %(message)s",
)
logger = logging.getLogger(settings.app_name)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

# Include the router
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    await ensure_collection_exists()
    logger.info("Indexing server started successfully")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
    )

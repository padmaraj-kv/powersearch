import logging
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    await ensure_collection_exists()
    logger.info("Indexing server started successfully")
    yield
    # Shutdown (if needed)
    # Add cleanup code here if required


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

# Include the router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
    )

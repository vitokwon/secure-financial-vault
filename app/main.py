from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Manager:
    Runs startup checks before accepting requests, and handles cleanup on shutdown.
    """
    # 1. Startup: Verify/create the isolated vault directory on disk
    storage_path = Path(settings.storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)
    print(f"[+] Bootstrapping complete. Storage directory verified at: {storage_path.resolve()}")

    yield

    # 2. Shutdown: Clean up background tasks or active connections if required
    print("[-] Application shutdown requested. Cleaning up resources...")


# Initialize the primary FastAPI application instance
app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url=f"{settings.api_v1_str}/docs",
    redoc_url=f"{settings.api_v1_str}/redoc",
    lifespan=lifespan,
)


@app.get("/health", tags=["System Telemetry"])
async def health_check():
    """
    Liveness probe to confirm the server is running and reading configuration correctly.
    """
    return {
        "status": "healthy",
        "project": settings.project_name,
        "api_version": settings.api_v1_str,
    }

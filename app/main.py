"""
app/main.py
Application Entrypoint: Configures FastAPI application lifecycle, registers domain routers,
and exposes OpenAPI documentation.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.domains.auth.router import router as auth_router
from app.domains.vault.router import router as vault_router
from app.telemetry.router import router as audit_router


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
    description="Enterprise-grade financial vault featuring AES-256-GCM encryption at rest, "
    "SHA-256 integrity verification, 3-tier JWT RBAC, and tamper-resistant audit trails.",
    version="1.0.0",
    docs_url=f"{settings.api_v1_str}/docs",
    redoc_url=f"{settings.api_v1_str}/redoc",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    lifespan=lifespan,
)

# Standard Security Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Domain Routers
app.include_router(auth_router, prefix=settings.api_v1_str)
app.include_router(vault_router, prefix=settings.api_v1_str)
app.include_router(audit_router, prefix=settings.api_v1_str)


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

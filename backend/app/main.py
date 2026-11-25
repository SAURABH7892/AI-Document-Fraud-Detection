"""FastAPI Application entrypoint for DocShield AI."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.db.session import engine, SessionLocal
from backend.app.db.init_db import init_db
from backend.app.api.v1.endpoints import auth, documents, verifications, dashboard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("docshield")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing DocShield AI database and services...")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("Startup complete. DocShield AI backend ready.")
    yield
    logger.info("DocShield AI backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="DocShield AI — AI-Based Document Fraud Detection and Verification System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])
app.include_router(verifications.router, prefix=f"{settings.API_V1_STR}/verifications", tags=["Verifications"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])

# Operational Endpoints
@app.get("/health", tags=["Operational"])
def health_check():
    """Liveness probe indicating service is running."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV
    }

@app.get("/ready", tags=["Operational"])
def readiness_check():
    """Readiness probe checking database connectivity."""
    db_healthy = False
    try:
        with engine.connect() as conn:
            conn.execute(conn.dialect.statement_compiler(conn.dialect, None).process(None)) if hasattr(conn, "ping") else None
            db_healthy = True
    except Exception as e:
        logger.warning(f"Database readiness probe failed: {e}")

    if not db_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "database": "disconnected"}
        )

    return {
        "status": "ready",
        "database": "connected",
        "storage": settings.STORAGE_TYPE,
        "worker_mode": settings.WORKER_MODE
    }

@app.get("/", tags=["Operational"])
def root_endpoint():
    return {
        "message": "Welcome to DocShield AI — AI-Based Document Fraud Detection and Verification System API",
        "docs": "/docs",
        "version": "1.0.0"
    }

"""Main FastAPI application entrypoint.

Initializes database tables, configures CORS middleware, registers routers,
and sets up OpenAPI metadata and health check endpoints.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import init_db
from app.routers import auth, expenses, totals


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown events."""
    # Initialize database tables on startup
    await init_db()
    yield


tags_metadata = [
    {
        "name": "Authentication",
        "description": "User registration, OAuth2 password login, and token generation.",
    },
    {
        "name": "Expenses",
        "description": (
            "Create, list, update, delete expenses, and filter by month, "
            "week, day, and category."
        ),
    },
    {
        "name": "Financial Totals & Salary",
        "description": "Record salary income and compute total expenses, salary, and remaining balance.",
    },
    {
        "name": "Health & Root",
        "description": "Service status and API entrypoints.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(totals.router)


@app.get("/", tags=["Health & Root"], summary="API Root")
async def root():
    """Welcome endpoint providing service status and link to interactive documentation."""
    return {
        "message": "Welcome to the Expense Management API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health", tags=["Health & Root"], summary="Health Check")
async def health_check():
    """Service health check endpoint returning operational status."""
    return {"status": "healthy"}
"""Configuration settings for the Expense Management Application.

Uses pydantic-settings to manage environment variables and application
configuration with sensible defaults.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""

    PROJECT_NAME: str = "Expense Management API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "A robust, asynchronous FastAPI application for tracking expenses, "
        "managing income/salary, calculating financial metrics, and filtering "
        "transactions with OAuth2 authentication."
    )
    API_V1_STR: str = ""

    # Database configuration (defaults to SQLite via aiosqlite)
    DATABASE_URL: str = "sqlite+aiosqlite:///./expenses.db"

    # Security & Authentication
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Whether authentication is strictly enforced on expenses and totals endpoints
    REQUIRE_AUTH: bool = True

    # CORS origins
    ALLOWED_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

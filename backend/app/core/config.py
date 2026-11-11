"""Application configuration using Pydantic Settings."""
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core App
    APP_NAME: str = "DocShield AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "docshield-local-development-secret-key-replace-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Network & CORS
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Database
    DATABASE_URL: str = "sqlite:///./docshield.db"

    # Storage
    STORAGE_TYPE: str = "local"  # "local" | "s3"
    STORAGE_LOCAL_PATH: str = "./storage"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: str = "docshield-documents"
    AWS_S3_ENDPOINT_URL: Optional[str] = None

    # Processing Worker
    WORKER_MODE: str = "inline"  # "inline" (threaded) | "celery"
    REDIS_URL: str = "redis://localhost:6379/0"

    # OCR
    OCR_ENGINE: str = "easyocr"  # "easyocr" | "fallback"
    OCR_GPU: bool = False

    # External Verification
    DIGILOCKER_ENABLED: bool = False
    DIGILOCKER_CLIENT_ID: Optional[str] = None
    DIGILOCKER_CLIENT_SECRET: Optional[str] = None
    DIGILOCKER_API_URL: str = "https://api.digitallocker.gov.in"

    # ML
    ML_MODEL_PATH: str = "ai/artifacts/docshield_classifier_v1.joblib"
    ML_CONFIDENCE_THRESHOLD: float = 0.5

settings = Settings()

import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesFlow CRM"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./salesflow.db",
        description="Database connection URL. In production, configure MySQL via DATABASE_URL.",
    )

    # JWT Authentication
    SECRET_KEY: str = Field(
        default="salesflow-crm-super-secret-key-change-in-production-2026",
        description="Secret key for signing JWT tokens",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS configuration - restricted origins specified via environment variable
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost",
        "http://127.0.0.1",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

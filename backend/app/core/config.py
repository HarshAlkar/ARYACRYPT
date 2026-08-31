import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo

# Never allow these fragments as JWT secrets (do not log the secret itself).
_FORBIDDEN_SECRET_FRAGMENTS = (
    "change-in-production",
    "your-super-secret",
    "secret-key-change",
    "changeme",
    "placeholder",
    "replace_with_output",
    "set_me",
    "paste_64_hex",
)

_MIN_SECRET_LENGTH = 32


def validate_secret_key(value: str) -> str:
    """Reject empty, short, or known-placeholder JWT secrets. Never echo the secret."""
    if value is None or not isinstance(value, str):
        raise ValueError(
            "SECRET_KEY is required. Generate one with: openssl rand -hex 32"
        )
    secret = value.strip()
    if not secret:
        raise ValueError(
            "SECRET_KEY must not be empty. Generate one with: openssl rand -hex 32"
        )
    if len(secret) < _MIN_SECRET_LENGTH:
        raise ValueError(
            f"SECRET_KEY must be at least {_MIN_SECRET_LENGTH} characters. "
            "Generate one with: openssl rand -hex 32"
        )
    lowered = secret.lower()
    for frag in _FORBIDDEN_SECRET_FRAGMENTS:
        if frag in lowered:
            raise ValueError(
                "SECRET_KEY looks like a documentation placeholder and is not allowed. "
                "Generate a random secret with: openssl rand -hex 32"
            )
    return secret


class Settings(BaseSettings):
    PROJECT_NAME: str = "AryaCrypt Backend API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    UPLOAD_DIR: str = "storage"
    VAULT_CAPACITY_BYTES: int = 5 * 1024 * 1024 * 1024
    MAX_UPLOAD_SIZE_BYTES: int = 100 * 1024 * 1024

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    AUTH_RATE_LIMIT_PER_MINUTE: int = 30
    DECRYPT_RATE_LIMIT_PER_MINUTE: int = 20
    # Set True behind HTTPS in production so the refresh cookie is not sent over cleartext.
    REFRESH_COOKIE_SECURE: bool = False

    BACKEND_CORS_ORIGINS: Union[List[AnyHttpUrl], str] = []

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def check_secret_key(cls, v: str) -> str:
        return validate_secret_key(v)

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: str | None = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                port=values.get("POSTGRES_PORT"),
                path=values.get("POSTGRES_DB") or "",
            )
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

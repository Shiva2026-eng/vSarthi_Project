from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str = "3fbf281f84f3576a851f56fd71c482928796d0bb9f60d63aaeacfd88967e74e3"
    ALGORITHM: str = "HS256"
    CLIENT_ID: Optional[str] = None
    CLIENT_SECRET: Optional[str] = None
    TENANT_ID: Optional[str] = "common"
    UPLOAD_DIR: str = "uploads"
    REDIRECT_URI: str = "http://localhost:8000/user/outlook/callback"
    DATABASE_URL: str = "sqlite:///./vsarthi_project.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Content Factory"
    environment: str = "development"
    secret_key: str = Field(min_length=32)
    database_url: str = "sqlite:///./app.db"
    storage_backend: str = "local"
    local_storage_root: str = "./data"
    gcs_bucket: str | None = None
    gcs_project_id: str | None = None
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

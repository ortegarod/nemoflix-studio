from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the agent-native API wrapper."""

    comfy_url: str = Field(default="http://127.0.0.1:8188", validation_alias="COMFY_URL")
    request_timeout_seconds: float = Field(default=120.0, validation_alias="REQUEST_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

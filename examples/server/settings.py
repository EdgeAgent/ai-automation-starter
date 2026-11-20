"""Environment-backed configuration shared by the API and Celery worker."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from process environment and an optional local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    api_token: SecretStr | None = Field(default=None, validation_alias="AI_STARTER_API_TOKEN")
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    model: str = Field(default="gpt-4o-mini", validation_alias="AI_STARTER_MODEL")
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="AI_STARTER_REDIS_URL",
    )

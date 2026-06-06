from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "nairi-api"
    version: str = "0.1.0"
    api_tokens: dict[str, list[str]] = Field(default_factory=dict)
    database_path: str = ":memory:"

    model_config = SettingsConfigDict(env_prefix="NAIRI_")


def get_settings() -> Settings:
    return Settings()

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "nairi-api"
    version: str = "0.1.0"
    api_tokens: dict[str, list[str]] = Field(default_factory=dict)
    database_path: str = ":memory:"
    public_invalidation_dispatcher: Literal["none", "contract", "cloudflare"] = "none"
    public_invalidation_cloudflare_zone_id: str | None = None
    public_invalidation_cloudflare_api_token: SecretStr | None = None

    model_config = SettingsConfigDict(env_prefix="NAIRI_")


def get_settings() -> Settings:
    return Settings()

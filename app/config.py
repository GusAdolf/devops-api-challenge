from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = "2f5ae96c-b558-4c7b-a590-a501ae1c3f6c"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DEVOPS_")


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://notary:notary@localhost:5432/notary"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-key"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

settings = Settings()

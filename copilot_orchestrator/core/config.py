from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings managed via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Project Info
    PROJECT_NAME: str = "copilot-orchestrator"
    VERSION: str = "0.0.0"
    ENVIRONMENT: str = "development"

    # API Configuration
    API_V1_STR: str = "/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # LLM Configuration
    OPENAI_API_KEY: SecretStr | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Infrastructure
    REDIS_URL: str = "redis://localhost:6379/0"

    # Data Layer (External)
    DATA_LAYER_BASE_URL: str = "http://localhost:8001"
    DATA_LAYER_API_KEY: SecretStr | None = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT_JSON: bool = True


settings = Settings()

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with environment variable support."""

    # API Server
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)

    # LLM Configuration
    OPENAI_API_KEY: str = Field(..., description="LLM API key")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")

    # Flash Model Configuration (for fast skill selection)
    FLASH_API_KEY: str | None = Field(default=None, description="Flash model API key")
    FLASH_BASE_URL: str | None = Field(default=None, description="Flash model base URL")
    FLASH_MODEL: str | None = Field(default=None, description="Flash model identifier")

    TEMPERATURE: float = Field(default=0.7)

    # Logging Configuration
    LOG_DIR: str = Field(default="logs")
    ENABLE_LOGGING: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()

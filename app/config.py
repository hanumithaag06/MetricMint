
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # Application configuration
    app_name: str = "metric-mint"
    environment: str = "local"  # local | ci | production

    # LLM provider configuration
    llm_provider: str = "fake"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = ""
    llm_model: str = "llama3.1:8b"

    # Reliability configuration
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    llm_backoff_base_seconds: float = 0.5

    # Token pricing per million tokens
    price_input_per_million: float = 0.0
    price_output_per_million: float = 0.0

    # Cost tracking
    cost_log_path: str = "logs/cost.jsonl"

    # Database configuration
    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()

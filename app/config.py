from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Knowledge Base
    kb_url: str = Field(..., description="URL da API do Knowledge Base")

    # LLM
    llm_provider: Literal["openai", "azure", "ollama"] = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"

    # Secret
    llm_api_key: SecretStr

    # Memory
    memory_store: str = ""

    # Server
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("llm_base_url")
    @classmethod
    def validate_base_url(cls, value: str):
        allowed_hosts = {
            "api.openai.com",
            "localhost",
            "127.0.0.1",
        }

        parsed = urlparse(value)

        if parsed.hostname not in allowed_hosts:
            raise ValueError(
                f"Endpoint não permitido: {parsed.hostname}"
            )

        return value


settings = Settings()

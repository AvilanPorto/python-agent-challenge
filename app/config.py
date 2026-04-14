from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kb_url: str
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str
    memory_store: str = ""
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()

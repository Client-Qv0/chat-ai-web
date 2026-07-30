from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ai_user:ai_password@localhost:5432/ai_platform"
    LLM_API_URL: str = "http://127.0.0.1:11434"
    LLM_MODEL: str = "qwen3.5:0.8b"
    SECRET_KEY: str = "change-me-to-a-random-secret-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://192.168.63.156:5173"]

    class Config:
        env_file = ".env"


settings = Settings()

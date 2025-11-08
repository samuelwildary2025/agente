from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TZ: str = "America/Sao_Paulo"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/superdb"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()

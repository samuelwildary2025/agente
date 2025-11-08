from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TZ: str = "America/Sao_Paulo"
    class Config:
        env_file = ".env"

settings = Settings()

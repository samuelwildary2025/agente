from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TZ: str = "America/Sao_Paulo"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/superdb"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Uazapi configuration
    UAZ_API_BASE: str = ""
    UAZ_INSTANCE_TOKEN: str = ""
    UAZ_ADMIN_TOKEN: str = ""
    # Paths are configurable to adapt to different Uazapi deployments
    UAZ_SEND_TEXT_PATH: str = "/message/text"
    UAZ_PRESENCE_PATH: str = "/presence/set"
    # Payload mode: 'number_text' (default) ou 'chatid_message'
    UAZ_PAYLOAD_MODE: str = "number_text"
    # Sufixo para chatId quando necessário (ex.: '@c.us')
    UAZ_CHATID_SUFFIX: str = "@c.us"

    class Config:
        env_file = ".env"

settings = Settings()

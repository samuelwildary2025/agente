from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json
from app.config import settings

def _normalize_db_url(url: str) -> str:
    # Compat com URLs comuns: "postgres://" e "postgresql://"
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    if url.startswith("postgres+asyncpg://"):
        return "postgresql+asyncpg://" + url[len("postgres+asyncpg://"):]
    return url

engine = create_async_engine(_normalize_db_url(settings.DATABASE_URL), echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def insert_cliente(session_id: str, content: str):
    async with SessionLocal() as session:
        payload = {"type": "human", "content": content, "additional_kwargs": {}, "response_metadata": {}}
        await session.execute(
            text("INSERT INTO dados_cliente (session_id, message) VALUES (:sid, :msg)"),
            {"sid": session_id, "msg": json.dumps(payload)},
        )
        await session.commit()

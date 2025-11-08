from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json

engine = create_async_engine("postgresql+asyncpg://user:password@postgres:5432/superdb", echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def insert_cliente(session_id: str, content: str):
    async with SessionLocal() as session:
        payload = {"type": "human", "content": content, "additional_kwargs": {}, "response_metadata": {}}
        await session.execute(
            text("INSERT INTO dados_cliente (session_id, message) VALUES (:sid, :msg)"),
            {"sid": session_id, "msg": json.dumps(payload)},
        )
        await session.commit()

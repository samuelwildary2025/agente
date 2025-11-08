import redis.asyncio as redis

from app.config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def msgs_key(tel: str) -> str:
    return f"msgs:{tel}"

def ativo_key(tel: str) -> str:
    return f"{tel}pedido"

def block_key(tel: str) -> str:
    return f"{tel}_block"

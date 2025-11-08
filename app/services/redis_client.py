import redis.asyncio as redis

from app.config import settings

r = redis.from_url("redis://redis:6379/0", decode_responses=True)

def msgs_key(tel: str) -> str:
    return f"msgs:{tel}"

def ativo_key(tel: str) -> str:
    return f"{tel}pedido"

def block_key(tel: str) -> str:
    return f"{tel}_block"

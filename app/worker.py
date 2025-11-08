import asyncio, orjson
from contextlib import suppress
from app.services.redis_client import r, msgs_key
from app.services.uaz import send_text, set_presence
from app.logic.agent import handle_dialog

async def pop_batch(tel: str) -> list[dict]:
    key = msgs_key(tel)
    items = []
    while True:
        item = await r.lpop(key)
        if not item:
            break
        items.append(orjson.loads(item))
    return items

async def process_tel(tel: str):
    await set_presence(tel, "composing", delay_ms=2000)
    batch = await pop_batch(tel)
    if not batch:
        return
    lines = [m.get("textMessage","") for m in batch if m.get("textMessage")]
    if not lines:
        return
    answer = await handle_dialog(tel, lines)
    with suppress(Exception):
        await send_text(tel, answer)

async def loop():
    window = 15.0
    while True:
        keys = await r.keys("msgs:*")
        if not keys:
            await asyncio.sleep(0.2)
            continue
        await asyncio.sleep(window)
        for key in keys:
            tel = key.split("msgs:",1)[1]
            try:
                await process_tel(tel)
            except Exception as e:
                await r.rpush("errors", str(e))

if __name__ == "__main__":
    asyncio.run(loop())

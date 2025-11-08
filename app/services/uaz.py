import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.5))
async def send_text(number: str, text: str):
    # placeholder simples
    return {"ok": True, "to": number, "text": text}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.5))
async def set_presence(number: str, presence: str = "composing", delay_ms: int = 2500):
    return {"ok": True}

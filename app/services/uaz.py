import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from app.config import settings

def _join(base: str, path: str) -> str:
    if not base:
        return path
    if base.endswith("/"):
        base = base[:-1]
    if not path.startswith("/"):
        path = "/" + path
    return base + path

def _default_headers(admin: bool = False) -> dict:
    hdrs = {"Accept": "application/json"}
    token = settings.UAZ_ADMIN_TOKEN if admin else settings.UAZ_INSTANCE_TOKEN
    if token:
        hdrs["admintoken" if admin else "token"] = token
    return hdrs

def _normalize_chatid(number: str) -> str:
    n = str(number).strip()
    # Se já contiver sufixo típico, mantém; senao, aplica o sufixo configurado
    if "@" in n:
        return n
    suffix = settings.UAZ_CHATID_SUFFIX or "@c.us"
    return f"{n}{suffix}"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.6))
async def send_text(number: str, text: str):
    """
    Envia texto via Uazapi.
    - Usa header 'token' (instância) e caminho configurável em UAZ_SEND_TEXT_PATH.
    - Payload padrão: {"number": <tel>, "text": <mensagem>}.
    """
    if not settings.UAZ_API_BASE or not settings.UAZ_INSTANCE_TOKEN:
        # Mantém comportamento tolerante para ambiente sem configuração
        return {"ok": True, "skipped": "missing UAZ config", "to": number, "text": text}

    url = _join(settings.UAZ_API_BASE, settings.UAZ_SEND_TEXT_PATH)
    chatid = _normalize_chatid(number)
    mode = (settings.UAZ_PAYLOAD_MODE or "number_text").lower()
    payloads = []
    if mode == "chatid_message":
        payloads = [{"chatId": chatid, "message": str(text)}]
    else:
        # Tenta primeiro number/text, depois chatId/message como fallback
        payloads = [{"number": str(number), "text": str(text)}, {"chatId": chatid, "message": str(text)}]

    async with httpx.AsyncClient(timeout=20) as client:
        last = None
        for p in payloads:
            r_ = await client.post(url, json=p, headers=_default_headers(admin=False))
            last = r_
            if r_.status_code < 400:
                try:
                    data = r_.json()
                except Exception:
                    data = {"status_code": r_.status_code, "text": r_.text}
                return {"ok": True, "response": data, "used_payload": p}
        # se nenhuma funcionou, levanta o ultimo erro
        last.raise_for_status()
        return {"ok": False, "status_code": last.status_code, "text": last.text}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.6))
async def set_presence(number: str, presence: str = "composing", delay_ms: int = 2500):
    """
    Seta presença/typing no chat.
    - Algumas instalações podem não suportar esse endpoint; em caso de 404, retorna ok.
    - Payload: {"number": <tel>, "presence": <estado>, "delay_ms": <int>}.
    """
    if not settings.UAZ_API_BASE or not settings.UAZ_INSTANCE_TOKEN:
        return {"ok": True, "skipped": "missing UAZ config"}

    url = _join(settings.UAZ_API_BASE, settings.UAZ_PRESENCE_PATH)
    payload = {"number": str(number), "presence": str(presence), "delay_ms": int(delay_ms)}
    async with httpx.AsyncClient(timeout=15) as client:
        r_ = await client.post(url, json=payload, headers=_default_headers(admin=False))
        if r_.status_code == 404:
            return {"ok": True, "skipped": "presence endpoint not available"}
        r_.raise_for_status()
        try:
            data = r_.json()
        except Exception:
            data = {"status_code": r_.status_code, "text": r_.text}
    return {"ok": True, "response": data}

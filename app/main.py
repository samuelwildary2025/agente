import orjson
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import WebhookPayload, DryRunInput
from app.services.redis_client import r, msgs_key, block_key
from app.services.uaz import set_presence, send_text
from app.services.postgres import insert_cliente
from app.logic.agent import handle_dialog

app = FastAPI(title="Supermarket Assistant Python")

def dumps(v) -> str:
    return orjson.dumps(v).decode()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/webhook/uaz")
async def webhook_uaz(req: Request):
    raw = await req.json()
    try:
        payload = WebhookPayload(**raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid payload: {e}")

    tel = payload.message.chatid
    bk = await r.get(block_key(tel))
    if bk:
        return JSONResponse({"ignored": "blocked"})

    try:
        await set_presence(tel, "composing", delay_ms=2500)
    except Exception:
        pass

    text = payload.message.content or ""
    if payload.message.messageType.lower() in ("audiomessage", "audio"):
        text = "[audio recebido]"

    try:
        await insert_cliente(session_id=tel, content=text)
    except Exception:
        pass

    await r.rpush(msgs_key(tel), dumps({"textMessage": text}))
    return {"queued": True}

@app.post("/agent/dryrun")
async def dryrun(inp: DryRunInput):
    lines = [l.strip() for l in (inp.listaMensagens or "").split("\n") if l.strip()]
    answer = await handle_dialog(inp.tel, lines)
    return {"answer": answer}

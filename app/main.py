import orjson, json
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

@app.get("/")
async def root():
    return {
        "service": "Supermarket Assistant API",
        "endpoints": ["GET /health", "POST /webhook/uaz", "POST /agent/dryrun", "GET /docs"],
    }

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/webhook/uaz")
async def webhook_uaz(req: Request):
    # Parser tolerante: aceita application/json, texto JSON, ou form com campo JSON
    async def parse_body() -> dict:
        ct = (req.headers.get("content-type") or "").lower()
        if "application/json" in ct:
            return await req.json()
        # tenta direto do corpo
        body = (await req.body()).decode("utf-8", "ignore").strip()
        if body:
            try:
                return json.loads(body)
            except Exception:
                pass
        # tenta como form
        try:
            form = await req.form()
            for key in ("payload", "data", "json", "body"):
                if key in form:
                    val = form[key]
                    if isinstance(val, bytes):
                        val = val.decode("utf-8", "ignore")
                    try:
                        return json.loads(val)
                    except Exception:
                        continue
        except Exception:
            pass
        raise HTTPException(status_code=400, detail="invalid payload: unable to parse body as JSON")

    def get_nested(d: dict, path: list[str]):
        cur = d
        for k in path:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(k)
            if cur is None:
                return None
        return cur

    def coalesce(*vals):
        for v in vals:
            if isinstance(v, str) and v.strip():
                return v.strip()
        return None

    raw = await parse_body()
    # tenta nosso schema oficial primeiro; se falhar, extrai campos essenciais de formatos alternativos
    try:
        payload = WebhookPayload(**raw)
        tel = payload.message.chatid
        mtype = (payload.message.messageType or "").lower()
        text = payload.message.content or ""
    except Exception:
        tel = coalesce(
            get_nested(raw, ["message", "chatid"]),
            raw.get("chatid"), raw.get("chatId"), raw.get("number"), raw.get("telefone"), raw.get("phone")
        )
        text = coalesce(
            get_nested(raw, ["message", "content"]),
            raw.get("content"), raw.get("text"), raw.get("body"), raw.get("message")
        ) or ""
        mtype = (coalesce(
            get_nested(raw, ["message", "messageType"]),
            raw.get("messageType"), raw.get("type"), get_nested(raw, ["chat", "wa_lastMessageType"])
        ) or "textmessage").lower()
        if not tel:
            raise HTTPException(status_code=400, detail="invalid payload: missing chatid/number")

    bk = await r.get(block_key(tel))
    if bk:
        return JSONResponse({"ignored": "blocked"})

    try:
        await set_presence(tel, "composing", delay_ms=2500)
    except Exception:
        pass

    if mtype in ("audiomessage", "audio"):
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

import httpx, re, json
from app.config import settings
from app.services.redis_client import r, ativo_key
from tenacity import retry, stop_after_attempt, wait_fixed

async def consult_ean(produto_nome: str) -> dict:
    key = f"ean_cache:{produto_nome.strip().lower()}"
    cached = await r.get(key)
    if cached:
        return json.loads(cached)
    ean = "7894900010015"
    data = {"ean": ean, "produto": produto_nome}
    await r.set(key, json.dumps(data), ex=3600)
    return data

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.4))
async def consult_estoque(ean: str) -> dict:
    url = f"http://45.178.95.233:5001/api/Produto/GetProdutosEAN/{ean}"
    async with httpx.AsyncClient(timeout=20) as client:
        r_ = await client.get(url, headers={"accept": "*/*"})
        r_.raise_for_status()
        return r_.json()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.5))
async def send_pedido(pedido_json: dict):
    url = f"https://wildhub-wildhub-sistema-supermercado.5mos1l.easypanel.host/api/pedidos/"
    async with httpx.AsyncClient(timeout=20) as client:
        r_ = await client.post(url, json=pedido_json, headers={"Authorization": "Bearer 000000", "Content-Type": "application/json"})
        r_.raise_for_status()
        return r_.json()

async def set_ativo(tel: str, ttl_seconds: int = 600):
    await r.setex(ativo_key(tel), ttl_seconds, "ativo")

async def get_ativo(tel: str) -> str | None:
    return await r.get(ativo_key(tel))

def only_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

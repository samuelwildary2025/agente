import re
from typing import List, Optional
from app.logic.rules import FRASES, format_item_line
from app.services.tools import consult_ean, consult_estoque, send_pedido, set_ativo, get_ativo, only_digits

def extract_product(lines: List[str]) -> Optional[str]:
    # pega a ultima linha textual nao vazia como referencia de produto
    for line in reversed(lines):
        t = line.strip()
        if t:
            return t
    return None

async def handle_dialog(tel: str, lines: List[str]) -> str:
    """
    Regras basicas que substituem o Agent do n8n:
    - Se cliente diz 'sim' apos resumo -> envia pedido e seta TTL.
    - Se menciona 'trocar', 'mudar', 'adicionar' -> verifica TTL e usa update.
    - Senao -> tenta entender produto, consultar EAN/estoque.
    """
    joined = " ".join([l.lower() for l in lines if l]).strip()

    # Edicao de pedido?
    if any(k in joined for k in ["trocar", "mudar", "adicionar", "incluir"]):
        ativo = await get_ativo(tel)
        if ativo == "ativo":
            return FRASES["edit_ttl"]
        else:
            return FRASES["edit_exp"]

    # Confirmacao explicita?
    if re.search(r"\b(sim|confirmo|fechar|pode fechar)\b", joined):
        prod = extract_product(lines) or "Item"
        ean_data = await consult_ean(prod)
        info = await consult_estoque(ean_data["ean"])
        preco = float(info.get("preco", 10.49))
        item = {"nome_produto": prod, "quantidade": 1, "preco_unitario": preco}
        total = item["quantidade"] * item["preco_unitario"]

        pedido = {
            "nome_cliente": "Cliente",
            "telefone": only_digits(tel),
            "endereco": "A combinar",
            "forma": "Entrega",
            "observacao": "",
            "itens": [item],
            "total": round(total, 2),
        }
        await send_pedido(pedido)
        await set_ativo(tel, ttl_seconds=600)
        return FRASES["confirmado"]

    # fluxo de produto
    prod = extract_product(lines)
    if not prod:
        return "Oi! Posso ajudar encontrando um produto pra voce?"
    try:
        ean_data = await consult_ean(prod)
        info = await consult_estoque(ean_data["ean"])
        preco = float(info.get("preco", 0))
        if preco > 0:
            return FRASES["produto_ok"].format(produto=prod, preco=preco) + " " + FRASES["forma"]
    except Exception:
        pass
    return FRASES["indisp"]

FRASES = {
    "produto_ok": "Tem sim! O {produto} esta saindo por R${preco:.2f}.",
    "indisp": "Nao encontrei esse item agora. Posso te indicar algo parecido?",
    "forma": "Vai querer retirar na loja ou entrega em casa?",
    "endereco": "Pode me passar rua, numero, bairro?",
    "resumo": "Ficou assim:\n{itens}\n- Forma: {forma}{endereco}\n- Total: R${total:.2f}\nPosso confirmar o pedido?",
    "confirmado": "Pedido confirmado! Nossa equipe vai separar tudo direitinho e te chama quando estiver pronto. Obrigado por comprar com a gente!",
    "edit_ttl": "Claro! Ainda da tempo de incluir. Qual item voce gostaria de adicionar?",
    "edit_exp": "Esse pedido ja esta sendo preparado para faturamento. Posso montar um novo pra voce, tudo bem?",
}

def format_item_line(qtd, nome, subtotal):
    return f"- {qtd}x {nome} — R${subtotal:.2f}"

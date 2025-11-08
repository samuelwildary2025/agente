from pydantic import BaseModel
from typing import Any, Optional, List

class MessageBody(BaseModel):
    chatid: str
    content: Optional[str] = ""
    messageTimestamp: int
    messageType: str
    messageid: str
    fromMe: bool = False

class ChatObj(BaseModel):
    wa_lastMessageType: Optional[str] = "Conversation"
    wa_contactName: Optional[str] = None

class WebhookPayload(BaseModel):
    BaseUrl: str
    EventType: str
    chat: ChatObj
    instanceName: str
    message: MessageBody
    owner: str
    token: str

class Item(BaseModel):
    nome_produto: str
    quantidade: int
    preco_unitario: float

class Pedido(BaseModel):
    nome_cliente: str
    telefone: str
    endereco: Optional[str] = None
    forma: str
    observacao: str = ""
    itens: List[Item]
    total: float

class DryRunInput(BaseModel):
    tel: str
    listaMensagens: str

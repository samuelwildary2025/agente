# Supermarket Assistant API – Integração Uazapi

Este projeto expõe um webhook de entrada (`POST /webhook/uaz`) e um worker que processa mensagens em fila do Redis, respondendo aos clientes via WhatsApp. A integração de envio de mensagens/presença é feita através da API Uazapi.

## Variáveis de Ambiente (Uazapi)

Configure no arquivo `.env` (ou nas variáveis da sua plataforma) os seguintes itens:

- `UAZ_API_BASE`: Base URL da sua API Uazapi. Ex.: `https://seu-uazapi.host`.
- `UAZ_INSTANCE_TOKEN`: Token da instância (header `token`). Ex.: `abc123...`.
- `UAZ_ADMIN_TOKEN` (opcional): Token administrativo (header `admintoken`).
- `UAZ_SEND_TEXT_PATH`: Caminho para envio de texto. Padrão: `/message/text`.
- `UAZ_PRESENCE_PATH`: Caminho para presença/typing. Padrão: `/presence/set`.
 - `UAZ_PAYLOAD_MODE`: Formato de payload de envio.
   - `number_text` (padrão): envia `{"number":"...","text":"..."}` e tenta fallback `{"chatId":"...@c.us","message":"..."}`.
   - `chatid_message`: usa diretamente `{"chatId":"...@c.us","message":"..."}`.
 - `UAZ_CHATID_SUFFIX`: Sufixo do `chatId` (ex.: `@c.us`).

Observação: Alguns servidores Uazapi usam caminhos diferentes. Ajuste os paths conforme sua documentação oficial: https://docs.uazapi.com/.

## Endpoints principais

- `GET /health` – saúde básica da API
- `POST /webhook/uaz` – recebe eventos do Uazapi e enfileira mensagens
- `POST /agent/dryrun` – simula respostas do agente para testes

## Worker de processamento

Para consumir a fila e enviar respostas pelo Uazapi, execute:

```
python -m app.worker
```

O worker lê mensagens do Redis e usa `app/services/uaz.py` (funções `send_text` e `set_presence`).

## Testes rápidos

1) Enviar payload de teste no Swagger (`/docs`) para `POST /webhook/uaz` usando o exemplo preenchido.
2) Ver a resposta `{"queued": true}`.
3) Com o worker rodando e o Uazapi configurado, a resposta do agente será enviada com `send_text` para o número do cliente.

### Mapeando com a documentação do Uazapi

Na doc do Uazapi (https://docs.uazapi.com/), copie:

- O caminho do endpoint de envio de texto e configure em `UAZ_SEND_TEXT_PATH`.
- O caminho do endpoint de presença (se existir) e configure em `UAZ_PRESENCE_PATH`.
- Verifique se o envio usa `header token` (instância) — já suportado.
- Se o payload esperado for `chatId`/`message`, ajuste `UAZ_PAYLOAD_MODE=chatid_message` e `UAZ_CHATID_SUFFIX=@c.us`.

## Observações

- Se `UAZ_API_BASE` ou `UAZ_INSTANCE_TOKEN` estiverem vazios, o serviço retorna `ok` com `skipped`, para não quebrar o fluxo de desenvolvimento. Configure as variáveis em produção.
- O parser do webhook é tolerante: aceita `application/json`, texto JSON e `x-www-form-urlencoded` com campos comuns (`payload`, `data`, `json`, `body`).

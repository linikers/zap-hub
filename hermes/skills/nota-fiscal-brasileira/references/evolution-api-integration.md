# Evolution API — WhatsApp para NFe Brasil

## Visão Geral

A **Evolution API** (evolution-foundation/evolution-api) é um servidor REST
completo para WhatsApp, baseado em Baileys. É a solução recomendada para
projetos NF-e que precisam de WhatsApp self-hosted na VPS.

**GitHub:** https://github.com/evolution-foundation/evolution-api  
**Docker:** `evoapicloud/evolution-api:latest`  
**Stars:** 8.700+ | **Forks:** 6.700+

## Comparação com Outras Soluções

| Aspecto | Cloud API (Meta) | Baileys Bridge | Evolution API |
|---------|:----------------:|:--------------:|:-------------:|
| setup   | Precisa app Meta | QR Code manual | QR Code + Dashboard |
| custo   | Gratuito (limites) | Gratuito | Gratuito |
| estabilidade | Alta | Média | Alta |
| dependência | Facebook/Meta | Node.js + Chrome | Docker |
| webhooks | Nativo | Manual | Nativo |
| dashboard | Não | Não | Sim (porta 8080) |
| múltiplos canais | WhatsApp só | WhatsApp só | WhatsApp + outros |

## Arquitetura no Monorepo nfe-brasil

```
WhatsApp Cliente
       ↓
Evolution API (:8080)
       ↓ webhook POST
whatsapp-bot (:3001)
       ↓
MCP Server (:8000) → 49 tools NF-e
```

## Docker Compose

```yaml
services:
  postgres:        # Database Evolution API (porta 5432)
  redis:           # Cache (porta 6379)
  evolution-api:   # WhatsApp server (porta 8080)
  mcp-server:      # NF-e tools (porta 8000)
  whatsapp-bot:    # Webhook handler (porta 3001)
```

## Setup na VPS

```bash
git clone https://github.com/linikers/nfe-brasil.git
cd nfe-brasil
docker-compose up -d

# Acessar dashboard
http://VPS:8080

# Criar instância
Nome: nfe-brasil
Tipo: Baileys (padrão)

# Conectar WhatsApp
Configurações → Aparelhos conectados → Conectar aparelho
Escanear QR Code exibido na dashboard
```

## Variáveis de Ambiente

### Evolution API (.env)
```env
SERVER_PORT=8080
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://evolution:senha@postgres:5432/evolution_db
WEBHOOK_GLOBAL_ENABLED=true
WEBHOOK_GLOBAL_URL=http://whatsapp-bot:3001/webhook/evolution
AUTHENTICATION_API_KEY=sua-chave-api
```

### WhatsApp Bot
```env
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=sua-chave-api
MCP_SERVER_URL=http://mcp-server:8000/mcp
WHATSAPP_RESTRICTED_MODE=true
```

## Formato do Webhook

A Evolution API envia POST para `/webhook/evolution`:

```json
{
  "event": "messages.upsert",
  "instance": "nfe-brasil",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "ABC123"
    },
    "message": {
      "conversation": "quero consultar nota fiscal"
    }
  }
}
```

### Eventos Disponíveis

| Evento | Descrição |
|--------|-----------|
| `messages.upsert` | Mensagem recebida |
| `messages.set` | Mensagem recebida (batch) |
| `connection.update` | Status da conexão |
| `qrcode.updated` | QR Code atualizado |
| `instance.create` | Instância criada |
| `instance.delete` | Instância removida |

## Envio de Mensagens

### Texto
```http
POST http://evolution-api:8080/message/sendText/nfe-brasil
Content-Type: application/json
apikey: sua-chave-api

{
  "number": "5511999999999",
  "text": "Olá! Recebi sua consulta."
}
```

### Arquivo (DANFE PDF, XML)
```http
POST http://evolution-api:8080/message/sendFile/nfe-brasil
Content-Type: application/json
apikey: sua-chave-api

{
  "number": "5511999999999",
  "filePath": "/tmp/DANFE_3521061498176200018755001000000023123456789.pdf"
}
```

## Autenticação

Todas as requisições devem incluir o header:
```
apikey: sua-chave-api
```

A API key é definida em `AUTHENTICATION_API_KEY` no .env da Evolution API.

## Vantagens para Projetos NF-e

1. **Dashboard inclusa** — visualiza mensagens, status, QR Code
2. **Webhook nativo** — não precisa de polling
3. **Persistence** — mensagens salvas no PostgreSQL
4. **Multi-instância** — pode rodar vários números simultaneamente
5. **Fallback Cloud API** — suporta WhatsApp Cloud API como alternativa
6. **Integrações** — Chatwoot, Typebot, n8n, OpenAI prontos

## Roadmap de Implementação

1. [x] Docker compose com Evolution API
2. [x] Webhook handler para receber mensagens
3. [x] Integração com MCP Server
4. [ ] Envio de DANFE como arquivo
5. [ ] Validação de XML via mensagem
6. [ ] Consulta SEFAZ em tempo real
7. [ ] Modo restrito (só NF-e)
8. [ ] Horário comercial

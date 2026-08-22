# NFe Brasil - Monorepo Setup

## Repositório
- https://github.com/linikers/nfe-brasil
- Base: DeHor-Labs/mcp-fiscal-brasil (MIT License)

## Estrutura
```
nfe-brasil/
├── mcp-server/              ← MCP Server (49 tools NF-e)
│   ├── src/nfe_brasil/
│   │   ├── nfe/             ← NF-e (parse, DANFE, assinatura, distribuição)
│   │   ├── nfse/            ← NFS-e (consulta municipal)
│   │   ├── cte/             ← CT-e (Conhecimento de Transporte)
│   │   ├── mdf_e/           ← MDF-e (Manifesto de Documentos)
│   │   ├── nfce/            ← NFC-e (Cupom Fiscal)
│   │   ├── sped/            ← SPED (EFD-ICMS, EFD-Contribuições)
│   │   ├── esocial/         ← eSocial
│   │   ├── agentic/         ← Reforma Tributária, compliance
│   │   ├── cnpj/            ← Consulta CNPJ
│   │   └── tabelas/         ← Tabelas offline (NCM, CFOP, CNAE)
│   └── pyproject.toml       ← Package name: nfe-brasil
├── whatsapp-bot/            ← WhatsApp Bot (Evolution API webhook)
│   ├── bridge/
│   │   ├── cloud_api.py     ← Cloud API webhook (porta 3001)
│   │   └── evolution_webhook.py ← Evolution API webhook (porta 3010)
│   ├── bot/nfe_handler.py   ← Handler NF-e
│   └── Dockerfile
├── shared/                  ← Documentação NF-e
│   ├── docs/
│   │   ├── codigos-retorno-sefaz.md
│   │   ├── contingencia.md
│   │   └── prazos-legais.md
│   └── scripts/
│       ├── backup-xml-email.py
│       └── organizar-xmls.py
├── evolution-api/.env       ← Config Evolution API
├── docker-compose.yml       ← 5 serviços
└── README.md
```

## Docker Compose (portas sem conflito)
| Serviço | Porta | Descrição |
|---------|-------|-----------|
| PostgreSQL | 5433 | Database Evolution API |
| Redis | 6380 | Cache |
| Evolution API | 8085 | WhatsApp server + Dashboard |
| MCP Server | 8090 | 49 tools NF-e |
| WhatsApp Bot | 3010 | Webhook handler |

## Setup na VPS
```bash
cd /root/nfe-brasil
docker compose up -d --build
```

## Testar serviços
```bash
# MCP Server
curl http://localhost:8090/mcp -H "Accept: text/event-stream"

# Bot health
curl http://localhost:3010/health

# Evolution API
curl http://localhost:8085/manager

# PostgreSQL
docker exec nfe-postgres psql -U evolution -d evolution_db -c "SELECT 1;"

# Redis
docker exec nfe-redis redis-cli ping
```

## Conectar WhatsApp (Evolution API)

### Pré-requisitos
- Containers rodando: `docker compose ps` (todos devem mostrar "Up")
- Verificar se já tem instância: `curl -H "apikey: nfe-...26" http://localhost:8085/instance/fetchInstances`
  - Retorna `[]` = nenhuma instância conectada
  - Retorna array com objeto = já tem instância

### Criar instância via API
```bash
API_KEY="nfe-brasil-2026"  # ajustar conforme docker-compose.yml

# 1. Criar instância
curl -X POST http://localhost:8085/instance/create/nfe-brasil \
  -H "apikey: $API_KEY" -H "Content-Type: application/json" \
  -d '{"integration": "WHATSAPP-BAILEYS"}'

# 2. Conectar (retorna QR code)
curl -H "apikey: $API_KEY" http://localhost:8085/instance/connect/nfe-brasil

# 3. Escanear QR com WhatsApp (Dispositivos conectados → Conectar dispositivo)

# 4. Verificar status (deve retornar "open" quando conectado)
curl -H "apikey: $API_KEY" http://localhost:8085/instance/connectionState/nfe-brasil
```

### Criar instância via Dashboard
1. Acessar http://SEU_IP:8085/manager
2. Login com API key
3. Criar instância com nome "nfe-brasil"
4. Escanear QR code gerado

### Verificar funcionamento
```bash
# Verificar que bot recebe mensagens (logs)
docker logs nfe-whatsapp-bot --tail 20

# Verificar que MCP server está healthy
curl http://localhost:8090/mcp -H "Accept: text/event-stream"

# Enviar mensagem de teste via WhatsApp do celular
```

## Bot persona (linguagem natural)
- Nunca mostrar CNPJ, chaves, códigos técnicos
- Respostas como atendente humano
- Envia PDF DANFE quando recebe XML
- Envia link SEFAZ quando consulta por chave
- Fora do horário: "Amanhã retorno! 😊"

## Portas em uso na VPS (evitar conflito)
- 22: SSH
- 5432: PostgreSQL (taiff)
- 5672: RabbitMQ
- 3000: Node.js
- 3001: Next.js (portfolio)
- 3002: Node.js
- 3004: Node.js
- 8765: Python
- 9119: Hermes
- 9120: AutoHedge

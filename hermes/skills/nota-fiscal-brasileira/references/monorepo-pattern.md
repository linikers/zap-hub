# Monorepo MCP Server + WhatsApp Bot

## Estrutura Recomendada

Para projetos NF-e que combinam MCP server + WhatsApp bot, use monorepo:

```
nfe-brasil/
├── mcp-server/              ← MCP Server (ferramentas)
│   ├── src/nfe_brasil/      ← Código fonte Python
│   │   ├── nfe/             ← NF-e (parse, DANFE, assinatura)
│   │   ├── nfse/            ← NFS-e
│   │   ├── cte/             ← CT-e (Conhecimento de Transporte)
│   │   ├── mdf_e/           ← MDF-e (Manifesto de Documentos)
│   │   ├── nfce/            ← NFC-e (Cupom Fiscal)
│   │   ├── sped/            ← SPED (EFD-ICMS, EFD-Contribuições)
│   │   ├── esocial/         ← eSocial
│   │   ├── agentic/         ← Reforma Tributária, compliance
│   │   ├── cnpj/            ← Consulta CNPJ
│   │   ├── tabelas/         ← Tabelas offline (NCM, CFOP, CNAE)
│   │   └── server.py        ← Registro das tools
│   ├── tests/               ← Testes
│   ├── Dockerfile
│   └── pyproject.toml
├── whatsapp-bot/            ← WhatsApp Bot
│   ├── bridge/
│   │   ├── evolution_webhook.py  ← Webhook Evolution API
│   │   └── cloud_api.py         ← Webhook Cloud API (opcional)
│   ├── bot/
│   │   └── nfe_handler.py   ← Lógica de processamento
│   ├── Dockerfile
│   └── requirements.txt
├── shared/                  ← Conhecimento compartilhado
│   ├── docs/                ← Documentação NF-e
│   ├── scripts/             ← Scripts auxiliares
│   └── templates/           ← Templates
├── evolution-api/           ← Configuração Evolution API
│   └── .env
├── docker-compose.yml       ← Deploy completo
├── README.md
└── LICENSE
```

## Docker Compose Base

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: evolution_db
      POSTGRES_USER: evolution
      POSTGRES_PASSWORD: senha
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  evolution-api:
    image: evoapicloud/evolution-api:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://evolution:***@postgres:5432/evolution_db
      - WEBHOOK_GLOBAL_URL=http://whatsapp-bot:3001/webhook/evolution
    depends_on:
      - postgres
      - redis

  mcp-server:
    build: ./mcp-server
    ports:
      - "8000:8000"
    environment:
      - FASTMCP_TRANSPORT=http

  whatsapp-bot:
    build: ./whatsapp-bot
    ports:
      - "3001:3001"
    environment:
      - MCP_SERVER_URL=http://mcp-server:8000/mcp
      - EVOLUTION_API_URL=http://evolution-api:8080
    depends_on:
      - mcp-server
      - evolution-api

volumes:
  postgres_data:
```

## Fluxo de Dados

```
Cliente WhatsApp
       ↓
Evolution API (porta 8080)
       ↓ webhook POST /webhook/evolution
whatsapp-bot (porta 3001)
       ↓ detectar_intencao_nfe()
       ↓
MCP Server (porta 8000)
       ↓ call_mcp_tool()
       ↓
49 tools (NF-e, CT-e, MDF-e, etc.)
       ↓
Resposta formatada
       ↓
Evolution API → Cliente WhatsApp
```

## Fork e Renomeação

Para forkar um MCP server existente e renomear:

1. Clone o repo original
2. Renomeie o diretório: `src/mcp_fiscal_brasil` → `src/nfe_brasil`
3. Atualize `pyproject.toml`:
   - `name = "nfe-brasil"`
   - `packages = ["src/nfe_brasil"]`
   - Entry points: `nfe-brasil = "nfe_brasil.server:main"`
4. Atualize imports: `find src -name '*.py' -exec sed -i 's/mcp_fiscal_brasil/nfe_brasil/g' {} +`
5. Teste: `pip install -e "." && python -c "from nfe_brasil import FiscalBrasil"`

## Boas Práticas

- **Separar responsabilidades**: MCP server = tools, WhatsApp bot = webhook handler
- **Shared code**: documentação e scripts ficam em `shared/`
- **Docker volumes**: persistir dados do PostgreSQL e instâncias da Evolution API
- **Health checks**: verificar se serviços estão rodando antes de dependências
- **API keys**: nunca commitar, usar .env + .gitignore

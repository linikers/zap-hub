# MCP Server Monorepo Pattern

## Repository Structure

```
nfe-brasil/
├── mcp-server/              ← MCP Server (Python, 49 tools)
│   ├── src/nfe_brasil/      ← Package source
│   ├── tests/
│   └── pyproject.toml
├── whatsapp-bot/            ← WhatsApp handler
│   ├── bridge/              ← Evolution API webhook
│   ├── bot/                 ← NF-e processing
│   └── requirements.txt
├── shared/                  ← Knowledge base
│   ├── docs/                ← NF-e documentation
│   ├── scripts/             ← Utility scripts
│   └── templates/
├── docker-compose.yml       ← All services
└── README.md
```

## Forking and Renaming a Python Package

When forking a repo and renaming the package:

1. Rename source directory: `mv src/mcp_fiscal_brasil src/nfe_brasil`
2. Update pyproject.toml: name, scripts, URLs
3. Mass update imports: `find src -name '*.py' -exec sed -i 's/mcp_fiscal_brasil/nfe_brasil/g' {} +`
4. Test: `pip install -e "." && python -c "from nfe_brasil import FiscalBrasil"`

## Docker Compose Port Allocation

Always check for port conflicts before deploying:

```bash
for port in 5432 6379 8080 8000 3001; do
    if ss -tlnp | grep -q ":$port "; then
        echo "PORT $port OCCUPIED"
    else
        echo "PORT $port FREE"
    fi
done
```

Common conflicts on this VPS:
- 5432: PostgreSQL (taiff-postgres container)
- 5672: RabbitMQ (rabbit-test container)
- 3000, 3001, 3002, 3004: Node.js services
- 8765: Python services
- 9119, 9120: Hermes / AutoHedge

Use offset ports: 5433, 6380, 8085, 8090, 3010

## Docker Compose v1 vs v2

docker-compose v1 (Python-based, 1.29.x) has issues with newer Docker versions.
Install docker compose v2 plugin (Go-based) instead:

```bash
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

Use `docker compose` (space) instead of `docker-compose` (hyphen).

## Healthcheck for MCP Servers

MCP servers return 406/400 for plain GET requests without proper headers.
Use `curl -s` (without `-f`) so the healthcheck doesn't fail on HTTP errors:

```yaml
healthcheck:
  test: ["CMD", "curl", "-s", "http://localhost:8000/mcp"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## PostgreSQL Password in Docker Compose

The terminal may censor passwords (displaying `***`). When writing docker-compose.yml
with passwords, use hex encoding in Python to avoid confusion:

```python
pwd = bytes.fromhex("6e66652d70672d32303236").decode()  # nfe-pg-2026
```

## New Modules (CT-e, MDF-e, NFC-e)

Each document type needs:
- `__init__.py` with exports
- `schemas.py` with Pydantic models
- `tools.py` with MCP tool functions
- Registration in `server.py`

## Evolution API Integration

See `whatsapp-cloud-api-bridge` skill for Evolution API setup.

Key points:
- REST API on port 8085
- Webhook to bot on port 3002
- QR code via REST endpoint
- PostgreSQL for persistence

## References

- github.com/linikers/nfe-brasil — Production repo
- github.com/DeHor-Labs/mcp-fiscal-brasil — Original fork (MIT)

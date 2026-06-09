# 📱 Zap Hub

**Gerenciamento centralizado de conexões WhatsApp.**

Unifica os dois esquemas de conexão usados nos projetos — Cloud API (Meta) e Baileys (QR Code) — com scripts, documentação e exemplos práticos baseados em casos reais.

## 🧠 Aprendizados (casos reais)

| Caso | Método | Ativação | Observação |
|------|--------|----------|------------|
| 🟢 **ML Atendente** | Cloud API | Rápida ✅ | Só precisou de token + webhook |
| 🟢 **Número Pessoal** | Cloud API | Rápida ✅ | Mesmo esquema, simples |
| 🔴 **NF-e Assistant** | Baileys QR | Enroscou ⚠️ | QR scan, sessão, daemon, tunnel |

**Conclusão:** sempre que possível, usar **Cloud API**. Baileys é o plano B quando a Cloud API não está disponível.

## 📂 Estrutura

```
zap-hub/
├── README.md                 ← Você está aqui
├── drivers/                  ← Métodos de conexão (ESCOLHA UM)
│   ├── cloud-api/            ← [RECOMENDADO] Meta Cloud API
│   │   ├── bridge.py          - Servidor webhook HTTP
│   │   └── .env.example       - Token, Phone ID, Account ID
│   └── baileys/              ← [PLANO B] Baileys QR Code
│       ├── bridge.js           - Bridge Node.js (conexão via QR)
│       ├── daemon.py           - Poller + processamento
│       ├── qr-server.py        - Servidor QR Code
│       └── .env.example        - Config da sessão
├── bots/                     ← Config de cada bot/assistente
│   ├── nfe/                   - NF-e Assistant (+55 44 991670539)
│   │   ├── .env
│   │   ├── run.sh
│   │   └── session/           - Sessão Baileys (gitignored)
│   ├── ml-atendente/          - Mercado Livre Atendente
│   │   ├── .env
│   │   └── run.sh
│   └── pessoal/               - Número pessoal
│       ├── .env
│       └── run.sh
├── scripts/                  ← Utilitários
│   ├── setup.sh               - Scaffold de nova instância
│   ├── tunnel.sh              - Inicia tunnel (localtunnel)
│   └── tunnel-watchdog.sh     - Tunnel com autoreconexão
└── .gitignore
```

## 🚀 Como usar

### Cloud API (recomendado)

```bash
# 1. Copie o env de exemplo
cp drivers/cloud-api/.env.example bots/meu-bot/.env

# 2. Preencha com suas credenciais (Token, Phone ID, Account ID)
#    (pegue em https://developers.facebook.com → App → WhatsApp)

# 3. Inicie
bash bots/meu-bot/run.sh start
```

### Baileys QR (plano B)

```bash
# 1. Configure o env
cp drivers/baileys/.env.example bots/meu-bot/.env

# 2. Inicie o bridge (QR code aparece no terminal)
bash bots/meu-bot/run.sh start

# 3. Escaneie o QR com o WhatsApp do número desejado
```

## 🔧 Tunnel (webhook)

A Cloud API precisa de um webhook público:

```bash
# Tunnel localhost.run (reconexão automática)
bash scripts/tunnel.sh <porta>

# Exemplo
bash scripts/tunnel.sh 3001
```

## 📋 Gestão de instâncias

Cada bot tem seu próprio `run.sh` com comandos padronizados:

```bash
bash bots/nfe/run.sh start      # Inicia
bash bots/nfe/run.sh stop       # Para
bash bots/nfe/run.sh status     # Status
bash bots/nfe/run.sh logs       # Logs
bash bots/nfe/run.sh qr         # Mostra QR (Baileys apenas)
```

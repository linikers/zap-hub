#!/usr/bin/env bash
# Setup — Cria uma nova instância de bot WhatsApp
# Uso: bash scripts/setup.sh <nome> <telefone> [driver] [porta]
#
# Drivers disponíveis:
#   cloud-api  — Meta Cloud API (RECOMENDADO, mais simples)
#   baileys    — Baileys QR Code (plano B)
#
# Exemplos:
#   bash scripts/setup.sh nfe 5544991670539 baileys 3003
#   bash scripts/setup.sh ml-atendente 5544998133182 cloud-api 3001
#   bash scripts/setup.sh pessoal 5544991234567 cloud-api 3002

set -e

HUB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NOME="${1}"
TELEFONE="${2}"
DRIVER="${3:-cloud-api}"
PORTA="${4:-3001}"

if [ -z "$NOME" ] || [ -z "$TELEFONE" ]; then
    echo "Uso: $0 <nome> <telefone> [driver] [porta]"
    echo ""
    echo "Drivers: cloud-api (padrao) | baileys"
    exit 1
fi

BOT_DIR="$HUB_DIR/bots/$NOME"
DRIVER_DIR="$HUB_DIR/drivers/$DRIVER"

if [ ! -d "$DRIVER_DIR" ]; then
    echo "Driver invalido: $DRIVER"
    echo "Disponiveis: cloud-api, baileys"
    ls -d "$HUB_DIR/drivers/"*/
    exit 1
fi

echo "=== Setup WhatsApp: $NOME ==="
echo "Telefone: +$TELEFONE"
echo "Driver: $DRIVER"
echo "Porta: $PORTA"
echo ""

# ── Criar diretório do bot ─────────────────────────────────────────────
mkdir -p "$BOT_DIR"
echo "[OK] Diretório: $BOT_DIR"

# ── Criar .env ─────────────────────────────────────────────────────────
ENV_FILE="$BOT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    echo "[OK] .env já existe"
else
    if [ "$DRIVER" = "cloud-api" ]; then
        cat > "$ENV_FILE" << EOF
# WhatsApp ${NOME} — Cloud API
# Telefone: +${TELEFONE}
export WHATSAPP_TOKEN=""
export WHATSAPP_PHONE_NUMBER_ID=""
export WHATSAPP_ACCOUNT_ID=""
export WHATSAPP_VERIFY_TOKEN="hermes_verify_123"
export WHATSAPP_BRIDGE_PORT="${PORTA}"
EOF
    else
        cat > "$ENV_FILE" << EOF
# WhatsApp ${NOME} — Baileys QR
# Telefone: +${TELEFONE}
export BOT_NAME="${NOME}"
export BOT_PHONE="${TELEFONE}"
export BRIDGE_PORT="${PORTA}"
export POLL_INTERVAL="2"
export BUSINESS_HOUR_START="8"
export BUSINESS_HOUR_END="18"
export BUSINESS_DAYS="1,2,3,4,5"
export BUSINESS_TZ="America/Sao_Paulo"
EOF
    fi
    echo "[CRIADO] $ENV_FILE"
fi

# ── Criar run.sh ───────────────────────────────────────────────────────
RUN_SCRIPT="$BOT_DIR/run.sh"
if [ -f "$RUN_SCRIPT" ]; then
    echo "[OK] run.sh já existe"
else
    if [ "$DRIVER" = "cloud-api" ]; then
        cat > "$RUN_SCRIPT" << 'SCRIPT'
#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HUB_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
BRIDGE_PY="$HUB_DIR/drivers/cloud-api/bridge.py"
PID_FILE="$SCRIPT_DIR/bridge.pid"
LOG_FILE="$SCRIPT_DIR/bridge.log"
VENV_PYTHON="/usr/local/lib/hermes-agent/venv/bin/python3"
start() {
  [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null && echo "Rodando" && exit 1
  [ -f "$ENV_FILE" ] && set -a && source "$ENV_FILE" && set +a
  nohup "$VENV_PYTHON" -u "$BRIDGE_PY" >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 2 && kill -0 "$(cat "$PID_FILE")" 2>/dev/null && echo "OK" || echo "FALHA"
}
stop() { [ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null && rm -f "$PID_FILE" && echo "Parado" || echo "Nao rodando"; }
status() { [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null && echo "Rodando" || echo "Parado"; }
logs() { [ -f "$LOG_FILE" ] && tail -f "$LOG_FILE" || echo "Sem logs"; }
case "${1:-status}" in start) start;; stop) stop;; restart) stop; sleep 1; start;; status) status;; logs) logs;; *) echo "Uso: $0 {start|stop|restart|status|logs}";; esac
SCRIPT
    else
        cat > "$RUN_SCRIPT" << 'SCRIPT'
#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HUB_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
BRIDGE_JS="$HUB_DIR/drivers/baileys/bridge.js"
DAEMON_PY="$HUB_DIR/drivers/baileys/daemon.py"
SESSION_DIR="$SCRIPT_DIR/session"
PORT="${BRIDGE_PORT:-3003}"
[ -f "$ENV_FILE" ] && set -a && source "$ENV_FILE" && set +a
start-bridge() {
  echo "Iniciando bridge..."
  mkdir -p "$SESSION_DIR"
  nohup node "$BRIDGE_JS" --port "$PORT" --session "$SESSION_DIR" --mode bot > "$SCRIPT_DIR/bridge.log" 2>&1 &
  echo $! > "$SCRIPT_DIR/bridge.pid"
  echo "Bridge na porta $PORT (PID $(cat "$SCRIPT_DIR/bridge.pid"))"
}
start-daemon() {
  cd "$SCRIPT_DIR"
  nohup python3 "$DAEMON_PY" > "$SCRIPT_DIR/daemon.log" 2>&1 &
  echo $! > "$SCRIPT_DIR/daemon.pid"
  echo "Daemon (PID $(cat "$SCRIPT_DIR/daemon.pid"))"
}
start) start-bridge; start-daemon;;
stop) 
  [ -f "$SCRIPT_DIR/daemon.pid" ] && kill "$(cat "$SCRIPT_DIR/daemon.pid")" 2>/dev/null; rm -f "$SCRIPT_DIR/daemon.pid"
  [ -f "$SCRIPT_DIR/bridge.pid" ] && kill "$(cat "$SCRIPT_DIR/bridge.pid")" 2>/dev/null; rm -f "$SCRIPT_DIR/bridge.pid"
  fuser -k "${PORT}/tcp" 2>/dev/null || true;;
qr) grep -A 15 "Scan this QR" "$SCRIPT_DIR/bridge.log" 2>/dev/null || echo "Ainda gerando...";;
status)
  echo "Bridge: $(curl -s http://localhost:$PORT/health 2>/dev/null | grep -o '"status":"[^"]*"' || echo 'offline')"
  echo "Daemon: $(kill -0 $(cat $SCRIPT_DIR/daemon.pid 2>/dev/null) 2>/dev/null && echo 'rodando' || echo 'parado')";;
logs) tail -f "$SCRIPT_DIR/bridge.log";;
daemon-logs) tail -f "$SCRIPT_DIR/daemon.log";;
*) echo "Uso: $0 {start|stop|status|qr|logs|daemon-logs}";;
esac
SCRIPT
    fi
    chmod +x "$RUN_SCRIPT"
    echo "[CRIADO] $RUN_SCRIPT"
fi

echo ""
echo "=== Setup concluído ==="
echo ""
echo "Próximos passos:"
if [ "$DRIVER" = "cloud-api" ]; then
    echo "1. Abrir https://developers.facebook.com → App → WhatsApp"
    echo "2. Adicionar número +${TELEFONE}"
    echo "3. Copiar TOKEN, PHONE_NUMBER_ID e ACCOUNT_ID"
    echo "4. Editar: nano $ENV_FILE"
    echo "5. Iniciar: bash $RUN_SCRIPT start"
else
    echo "1. Editar: nano $ENV_FILE (se precisar ajustar)"
    echo "2. Iniciar: bash $RUN_SCRIPT start"
    echo "3. Escanear QR Code com o WhatsApp do número +${TELEFONE}"
fi

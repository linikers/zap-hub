#!/usr/bin/env bash
# WhatsApp Cloud API — Número Pessoal
# Uso: ./run.sh {start|stop|status|restart|logs}
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HUB_DIR="$(cd "$BOTS_DIR/.." && pwd)"

ENV_FILE="$SCRIPT_DIR/.env"
BRIDGE_PY="$HUB_DIR/drivers/cloud-api/bridge.py"
PID_FILE="$SCRIPT_DIR/bridge.pid"
LOG_FILE="$SCRIPT_DIR/bridge.log"
VENV_PYTHON="/usr/local/lib/hermes-agent/venv/bin/python3"

start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Bridge já rodando (PID $(cat "$PID_FILE"))"
        exit 1
    fi
    echo "Iniciando WhatsApp Cloud API Bridge..."
    [ -f "$ENV_FILE" ] && set -a && source "$ENV_FILE" && set +a
    nohup "$VENV_PYTHON" -u "$BRIDGE_PY" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 2
    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "✓ Bridge started (PID $(cat "$PID_FILE"))"
        echo "  Logs: $LOG_FILE"
    else
        echo "✗ Bridge failed. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
    fi
}

stop() {
    [ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null && rm -f "$PID_FILE" && echo "Parado" || echo "Não rodando"
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Status: RODANDO (PID $(cat "$PID_FILE"))"
    else
        echo "Status: PARADO"
    fi
}

logs() { [ -f "$LOG_FILE" ] && tail -f "$LOG_FILE" || echo "Sem logs"; }

case "${1:-status}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 1; start ;;
    status) status ;;
    logs) logs ;;
    *) echo "Uso: $0 {start|stop|restart|status|logs}" ;;
esac

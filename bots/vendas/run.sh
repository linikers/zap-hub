#!/usr/bin/env bash
# WhatsApp Cloud API Bot — Vendas (Hermes como vendedor)
# Uso: ./run.sh {start|stop|status|restart|logs}
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HUB_DIR="$(cd "$BOTS_DIR/.." && pwd)"

ENV_FILE="$SCRIPT_DIR/.env"
BRIDGE_PY="$SCRIPT_DIR/bridge.py"
PID_FILE="$SCRIPT_DIR/bridge.pid"
LOG_FILE="$SCRIPT_DIR/bridge.log"
VENV_PYTHON="/usr/local/lib/hermes-agent/venv/bin/python3"
QUEUE_FILE="$SCRIPT_DIR/queue.json"

start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Bridge já rodando (PID $(cat "$PID_FILE"))"
        exit 1
    fi

    echo "Iniciando WhatsApp Cloud API Bridge — VENDAS..."

    [ -f "$ENV_FILE" ] && set -a && source "$ENV_FILE" && set +a

    # Export HERMES_PERSONA para o bridge usar personalidade de vendas
    export HERMES_PERSONA="--personality vendas"

    nohup "$VENV_PYTHON" -u "$BRIDGE_PY" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    # Inicializa fila de leads
    echo '[]' > "$QUEUE_FILE" 2>/dev/null || true

    sleep 2
    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "✓ Bridge vendas started (PID $(cat "$PID_FILE"))"
        echo "  Logs: $LOG_FILE"
        echo "  Leads: $QUEUE_FILE"
    else
        echo "✗ Bridge failed to start. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Bridge não rodando (sem PID file)"
        return
    fi

    PID=$(cat "$PID_FILE")
    echo "Parando bridge (PID $PID)..."
    kill "$PID" 2>/dev/null && echo "✓ Parado" || echo "× Não rodando"
    rm -f "$PID_FILE"
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "✓ Rodando (PID $(cat "$PID_FILE"))"
    else
        echo "× Parado"
    fi
}

logs() {
    tail -f "$LOG_FILE"
}

case "${1:-status}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 1; start ;;
    status) status ;;
    logs) logs ;;
    *)
        echo "Uso: $0 {start|stop|status|restart|logs}"
        exit 1
        ;;
esac

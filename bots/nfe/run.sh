#!/usr/bin/env bash
# WhatsApp NF-e — Bridge para +55 44 991670539
# Modo Bot: recebe mensagens externas (QR Code via Baileys)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HUB_DIR="$(cd "$BOTS_DIR/.." && pwd)"

BRIDGE_JS="$HUB_DIR/drivers/baileys/bridge.js"
DAEMON_PY="$HUB_DIR/drivers/baileys/daemon.py"
SESSION_DIR="$SCRIPT_DIR/session"
ENV_FILE="$SCRIPT_DIR/.env"
BRIDGE_LOG="$SCRIPT_DIR/bridge.log"
DAEMON_LOG="$SCRIPT_DIR/daemon.log"
DAEMON_PID="$SCRIPT_DIR/daemon.pid"
BRIDGE_PID="$SCRIPT_DIR/bridge.pid"

# Load env
[ -f "$ENV_FILE" ] && set -a && source "$ENV_FILE" && set +a

PORT="${BRIDGE_PORT:-3003}"

case "${1:-status}" in
  start-bridge)
    echo "=== Iniciando Bridge (Baileys) ==="
    mkdir -p "$SESSION_DIR"
    nohup node "$BRIDGE_JS" \
      --port "$PORT" \
      --session "$SESSION_DIR" \
      --mode bot \
      > "$BRIDGE_LOG" 2>&1 &
    echo $! > "$BRIDGE_PID"
    echo "Bridge iniciada (PID $(cat $BRIDGE_PID)) na porta $PORT"
    echo ""
    echo "=== QR CODE ==="
    echo "Com o celular cadastrado:"
    echo "1. Abra o WhatsApp > Configurações > Dispositivos conectados"
    echo "2. Toque em 'Conectar um dispositivo'"
    echo "3. Escaneie o QR abaixo:"
    echo ""
    grep -A 15 "Scan this QR" "$BRIDGE_LOG" 2>/dev/null || echo "(Gerando QR... rode './run.sh qr' em 10s)"
    echo ""
    echo "Log: tail -f $BRIDGE_LOG"
    ;;

  start-daemon)
    echo "=== Iniciando Daemon ==="
    cd "$SCRIPT_DIR"
    nohup python3 "$DAEMON_PY" > "$DAEMON_LOG" 2>&1 &
    echo $! > "$DAEMON_PID"
    echo "Daemon iniciado (PID $(cat $DAEMON_PID))"
    ;;

  start)
    bash "$0" start-bridge
    bash "$0" start-daemon
    ;;

  stop)
    echo "=== Parando ==="
    [ -f "$DAEMON_PID" ] && kill "$(cat "$DAEMON_PID")" 2>/dev/null && rm -f "$DAEMON_PID" && echo "Daemon parado"
    [ -f "$BRIDGE_PID" ] && kill "$(cat "$BRIDGE_PID")" 2>/dev/null && rm -f "$BRIDGE_PID" && echo "Bridge parada"
    fuser -k "${PORT}/tcp" 2>/dev/null || true
    ;;

  qr)
    echo "=== QR CODE ==="
    grep -A 15 "Scan this QR" "$BRIDGE_LOG" 2>/dev/null || echo "Ainda não gerado. Rode primeiro: ./run.sh start-bridge"
    ;;

  status)
    echo "Bridge: $(curl -s http://localhost:$PORT/health 2>/dev/null | grep -o '"status":"[^"]*"' || echo 'offline')"
    echo "Daemon: $(kill -0 $(cat $DAEMON_PID 2>/dev/null) 2>/dev/null && echo 'rodando' || echo 'parado')"
    echo "Session: $(ls $SESSION_DIR 2>/dev/null | wc -l) arquivos"
    ;;

  logs) tail -f "$BRIDGE_LOG" ;;
  daemon-logs) tail -f "$DAEMON_LOG" ;;
  *)
    echo "Uso: $0 {start|stop|status|qr|logs|daemon-logs}"
    echo ""
    echo "  start        - Inicia bridge + daemon"
    echo "  stop         - Para tudo"
    echo "  status       - Status"
    echo "  qr           - Mostra QR Code"
    echo "  logs         - Log da bridge (QR aparece aqui)"
    ;;
esac

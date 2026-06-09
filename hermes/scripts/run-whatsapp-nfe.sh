#!/usr/bin/env bash
# WhatsApp NF-e — Bridge para +55 44 991670539
# Modo Bot: recebe mensagens externas (nao precisa ser self-chat)
# QR Code: gerado na primeira execucao, exibido no log

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIDGE_DIR="/usr/local/lib/hermes-agent/scripts/whatsapp-bridge"
SESSION_DIR="$SCRIPT_DIR/whatsapp-nfe-session"
BRIDGE_LOG="$SCRIPT_DIR/whatsapp-nfe-bridge.log"
DAEMON_LOG="$SCRIPT_DIR/whatsapp-nfe-daemon.log"
DAEMON_PID="$SCRIPT_DIR/whatsapp-nfe-daemon.pid"
BRIDGE_PID="$SCRIPT_DIR/whatsapp-nfe-bridge.pid"

case "${1:-status}" in
  start-bridge)
    echo "=== NFC-e Bridge ==="
    mkdir -p "$SESSION_DIR"
    cd "$BRIDGE_DIR"
    nohup node bridge.js \
      --port 3003 \
      --session "$SESSION_DIR" \
      --mode bot \
      > "$BRIDGE_LOG" 2>&1 &
    echo $! > "$BRIDGE_PID"
    echo "Bridge iniciada (PID $(cat $BRIDGE_PID))"
    echo "Aguardando QR Code..."
    sleep 8
    echo ""
    echo "=== QR CODE ==="
    echo "Com o celular com o chip +55 44 991670539:"
    echo "1. Abra o WhatsApp > Configuracões > Dispositivos conectados"
    echo "2. Toque em 'Conectar um dispositivo'"
    echo "3. Escaneie o QR abaixo:"
    echo ""
    grep -A 15 "Scan this QR" "$BRIDGE_LOG" || echo "(Ainda gerando... rode 'qr' novamente em 10s)"
    echo ""
    echo "Log completo: tail -f $BRIDGE_LOG"
    ;;

  start-daemon)
    echo "=== NFC-e Daemon ==="
    cd "$SCRIPT_DIR"
    nohup python3 whatsapp-nfe-daemon.py > "$DAEMON_LOG" 2>&1 &
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
    fuser -k 3003/tcp 2>/dev/null || true
    ;;

  qr)
    echo "=== QR CODE ==="
    grep -A 15 "Scan this QR" "$BRIDGE_LOG" 2>/dev/null || echo "Ainda nao gerado. Rode: tail -f $BRIDGE_LOG"
    ;;

  status)
    echo "Bridge: $(curl -s http://localhost:3003/health 2>/dev/null | grep -o '"status":"[^"]*"' || echo 'offline')"
    echo "Daemon: $(kill -0 $(cat $DAEMON_PID 2>/dev/null) 2>/dev/null && echo 'rodando' || echo 'parado')"
    echo "Session files: $(ls $SESSION_DIR 2>/dev/null | wc -l)"
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

#!/usr/bin/env bash
# WhatsApp Cloud API Bridge - Start script
# Use: ./run-whatsapp-cloud.sh [start|stop|restart|status|logs]

BRIDGE_DIR="$(dirname "$0")"
ENV_FILE="$BRIDGE_DIR/whatsapp-cloud.env"
BRIDGE_SCRIPT="$BRIDGE_DIR/whatsapp-cloud-bridge.py"
PID_FILE="$BRIDGE_DIR/whatsapp-cloud.pid"
LOG_FILE="$BRIDGE_DIR/whatsapp-cloud.log"
VENV_PYTHON="/usr/local/lib/hermes-agent/venv/bin/python3"

start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "WhatsApp Cloud Bridge already running (PID $(cat "$PID_FILE"))"
        exit 1
    fi

    echo "Starting WhatsApp Cloud Bridge..."
    
    # Source env vars and start
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
    fi
    
    nohup "$VENV_PYTHON" -u "$BRIDGE_SCRIPT" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "✓ Bridge started (PID $(cat "$PID_FILE"))"
        echo "  Health: http://localhost:${WHATSAPP_BRIDGE_PORT:-3001}/health"
        echo "  Logs: $LOG_FILE"
    else
        echo "✗ Bridge failed to start. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Bridge not running (no PID file)"
        return
    fi
    
    PID=$(cat "$PID_FILE")
    echo "Stopping WhatsApp Cloud Bridge (PID $PID)..."
    kill "$PID" 2>/dev/null && echo "✓ Stopped" || echo "× Not running"
    rm -f "$PID_FILE"
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "WhatsApp Cloud Bridge: RUNNING (PID $(cat "$PID_FILE"))"
        curl -s http://localhost:${WHATSAPP_BRIDGE_PORT:-3001}/health 2>/dev/null || echo "(health check failed)"
    else
        echo "WhatsApp Cloud Bridge: STOPPED"
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "No log file found"
    fi
}

case "${1:-start}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 1; start ;;
    status) status ;;
    logs) logs ;;
    *)
        echo "Usage: $0 [start|stop|restart|status|logs]"
        exit 1
        ;;
esac

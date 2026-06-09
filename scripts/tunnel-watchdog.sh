#!/usr/bin/env bash
# Tunnel watchdog — mantém o tunnel ativo com autoreconexão
# Uso: bash scripts/tunnel-watchdog.sh [porta]
set -e
PORT="${1:-3001}"
TUNNEL_LOG="/tmp/zap-hub-tunnel.log"
URL_FILE="/tmp/zap-hub-tunnel-url.txt"
rm -f "$URL_FILE"

log() { echo "[$(date '+%H:%M:%S')] $*" >> "$TUNNEL_LOG"; }
log "Watchdog iniciado na porta $PORT"

while true; do
    log "Conectando tunnel..."
    ssh -o StrictHostKeyChecking=no \
        -o ServerAliveInterval=15 \
        -o ServerAliveCountMax=3 \
        -o ExitOnForwardFailure=yes \
        -R 80:localhost:$PORT \
        nokey@localhost.run 2>&1 | while read line; do
            echo "$line" >> "$TUNNEL_LOG"
            if [[ "$line" =~ https://([a-z0-9]+\.lhr\.life) ]]; then
                URL="${BASH_REMATCH[0]}"
                echo "$URL" > "$URL_FILE"
                log "TUNNEL URL: $URL"
            fi
        done
    log "Tunnel desconectado. Reconectando em 5s..."
    sleep 5
done

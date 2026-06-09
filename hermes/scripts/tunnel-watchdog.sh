#!/usr/bin/env bash
# Tunnel watchdog - keeps the localhost.run tunnel up
# Writes URL to /tmp/tunnel-url.txt

TUNNEL_LOG="/tmp/tunnel-watchdog.log"
URL_FILE="/tmp/tunnel-url.txt"
BRIDGE_PORT="${1:-3001}"

log() {
    echo "[$(date '+%H:%M:%S')] $*" >> "$TUNNEL_LOG"
}

rm -f "$URL_FILE"
log "Starting tunnel watchdog on port $BRIDGE_PORT..."

while true; do
    log "Connecting tunnel..."
    
    # SSH with localhost.run
    ssh -o StrictHostKeyChecking=no \
        -o ServerAliveInterval=15 \
        -o ServerAliveCountMax=3 \
        -o ExitOnForwardFailure=yes \
        -R 80:localhost:$BRIDGE_PORT \
        nokey@localhost.run 2>&1 | while read line; do
            echo "$line" >> "$TUNNEL_LOG"
            # Extract URL
            if [[ "$line" =~ https://([a-z0-9]+\.lhr\.life) ]]; then
                URL="${BASH_REMATCH[0]}"
                echo "$URL" > "$URL_FILE"
                log "TUNNEL URL: $URL"
            fi
        done
    
    log "Tunnel disconnected. Reconnecting in 5s..."
    sleep 5
done

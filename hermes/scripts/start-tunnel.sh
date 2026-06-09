#!/usr/bin/env bash
# Tunnel starter - saves URL to file
TUNNEL_LOG="/tmp/tunnel-url.txt"
rm -f "$TUNNEL_LOG"
npx -y localtunnel --port 3001 2>&1 | tee "$TUNNEL_LOG"

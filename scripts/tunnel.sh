#!/usr/bin/env bash
# Inicia tunnel (localtunnel) para webhook
# Uso: bash scripts/tunnel.sh [porta]
set -e
PORT="${1:-3001}"
echo "Iniciando tunnel na porta $PORT..."
echo "URL vai aparecer abaixo:"
npx -y localtunnel --port "$PORT"

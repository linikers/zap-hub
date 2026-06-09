#!/usr/bin/env bash
# WhatsApp Cloud API - Setup Padronizado
# Uso: bash setup-whatsapp-numero.sh <nome> <telefone> [porta]
#
# Exemplo:
#   bash setup-whatsapp-numero.sh nfe "5544991670539" 3002
#   bash setup-whatsapp-numero.sh carcrew "5544998133182" 3003

set -e

NOME="${1:-nfe}"
TELEFONE="${2:-5544991670539}"
PORTA="${3:-3002}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Setup WhatsApp: $NOME ==="
echo "Telefone: +$TELEFONE"
echo "Porta: $PORTA"
echo ""

# ── 1. Arquivo .env ──────────────────────────────────────────────────
ENV_FILE="$SCRIPT_DIR/whatsapp-${NOME}.env"
if [ -f "$ENV_FILE" ]; then
  echo "[OK] .env já existe: $ENV_FILE"
else
  cat > "$ENV_FILE" << EOF
#!/usr/bin/env bash
# WhatsApp - ${NOME}
# Telefone: +${TELEFONE}
export WHATSAPP_TOKEN=""
export WHATSAPP_PHONE_NUMBER_ID=""
export WHATSAPP_ACCOUNT_ID=""
export WHATSAPP_VERIFY_TOKEN="hermes_verify_123"
export WHATSAPP_BRIDGE_PORT="${PORTA}"
export WHATSAPP_RESTRICTED_MODE="true"
export NFE_BUSINESS_HOUR_START="8"
export NFE_BUSINESS_HOUR_END="18"
export NFE_BUSINESS_DAYS="1,2,3,4,5"
export NFE_BUSINESS_TZ="America/Sao_Paulo"
EOF
  echo "[CRIADO] $ENV_FILE"
fi

# ── 2. Script de gerenciamento ───────────────────────────────────────
RUN_SCRIPT="$SCRIPT_DIR/run-whatsapp-${NOME}.sh"
if [ -f "$RUN_SCRIPT" ]; then
  echo "[OK] Script já existe: $RUN_SCRIPT"
else
  cat > "$RUN_SCRIPT" << 'SCRIPT'
#!/usr/bin/env bash
# WhatsApp - gerenciamento
NOME="__NOME__"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/whatsapp-${NOME}.env"
BRIDGE="$SCRIPT_DIR/whatsapp-cloud-bridge.py"
LOG="$SCRIPT_DIR/whatsapp-${NOME}.log"
PID_FILE="$SCRIPT_DIR/whatsapp-${NOME}.pid"

case "${1:-status}" in
  start)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "${NOME} já rodando (PID $(cat "$PID_FILE"))"
      exit 0
    fi
    echo "Iniciando ${NOME}..."
    source "$ENV_FILE"
    nohup python3 -u "$BRIDGE" >> "$LOG" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 2
    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "OK - PID $(cat "$PID_FILE")"
    else
      echo "FALHA"
      tail -3 "$LOG"
      exit 1
    fi
    ;;
  stop)
    [ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null && rm -f "$PID_FILE" && echo "${NOME} parado" || echo "Não rodando"
    ;;
  restart) "$0" stop; sleep 1; "$0" start ;;
  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      PORTA=$(grep BRIDGE_PORT "$ENV_FILE" | cut -d= -f2)
      echo "Rodando - PID $(cat "$PID_FILE") na porta $PORTA"
    else
      echo "Parado"
    fi
    ;;
  logs) tail -f "$LOG" ;;
  *) echo "Uso: $0 {start|stop|restart|status|logs}" ;;
esac
SCRIPT
  sed -i "s/__NOME__/$NOME/g" "$RUN_SCRIPT"
  chmod +x "$RUN_SCRIPT"
  echo "[CRIADO] $RUN_SCRIPT"
fi

echo ""
echo "=== Setup concluído ==="
echo ""
echo "Próximos passos (quando tiver o telefone):"
echo "1. Abrir https://developers.facebook.com"
echo "2. App → WhatsApp → Configuration → Adicionar número +${TELEFONE}"
echo "3. Copiar TOKEN, PHONE_NUMBER_ID e ACCOUNT_ID"
echo "4. Editar: nano $ENV_FILE"
echo "5. Iniciar: bash $RUN_SCRIPT start"
echo "6. Configurar webhook (ngrok/Cloudflare)"

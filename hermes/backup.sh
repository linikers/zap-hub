#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# zap-hub Backup — Exporta estado do Hermes Agent para o repositório
# ═══════════════════════════════════════════════════════════════════════
# Uso: bash hermes/backup.sh
#
# O que salva:
#   skills/   → ~/.hermes/skills/ (procedural memory)
#   memories/ → ~/.hermes/memories/ (user profile + agent notes)
#   config/   → ~/.hermes/config.yaml (sem secrets)
#   crons/    → Lista de cron jobs ativos
#   facts/    → Holographic memory facts (se fact_store disponível)
# ═══════════════════════════════════════════════════════════════════════
set -e

HUB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$HUB_DIR/hermes"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

echo "=== Zap-Hub Backup ==="
echo "Hermes home: $HERMES_HOME"
echo "Backup dir: $BACKUP_DIR"
echo ""

# ── Skills (so as nossas, nao as built-in do Hermes) ─────────────────
echo "[1/6] Skills customizadas..."
rm -rf "$BACKUP_DIR/skills"
mkdir -p "$BACKUP_DIR/skills"
if [ -d "$HERMES_HOME/skills" ]; then
  # Skills que criamos/modificamos (exclui as built-in que vem com o Hermes)
  # Lista manual pra nao copiar 500MB de skills padrao
  for skill in \
    nota-fiscal-brasileira \
    brazilian-payment-gateways \
    twitter-algorithm-optimizer \
    content-research-writer \
    mercado-livre-clientes \
    persona-vendedor-curso-web3 \
    persona-assistente-nfe \
    persona-psicologo-inner \
    xurl \
    impeccable \
    nextjs-seo \
    nextjs-mui \
    systematic-debugging \
    react-i18n \
    nextjs-ai-routes \
    nextjs-project-cleanup \
    ocr-and-documents \
    backend-notification-service \
    debugging-hermes-tui-commands; do
    if [ -d "$HERMES_HOME/skills/$skill" ]; then
      cp -r "$HERMES_HOME/skills/$skill" "$BACKUP_DIR/skills/" 2>/dev/null
      echo "  → $skill"
    fi
  done
  echo "  Total: $(ls "$BACKUP_DIR/skills" 2>/dev/null | wc -l) skills"
else
  echo "  ⚠ Nenhuma skill encontrada"
fi

# ── Memories ──────────────────────────────────────────────────────────
echo "[2/5] Memories..."
mkdir -p "$BACKUP_DIR/memories"
if [ -f "$HERMES_HOME/memories/MEMORY.md" ]; then
  cp "$HERMES_HOME/memories/MEMORY.md" "$BACKUP_DIR/memories/MEMORY.md"
  echo "  → MEMORY.md salvo"
fi
if [ -f "$HERMES_HOME/memories/USER.md" ]; then
  cp "$HERMES_HOME/memories/USER.md" "$BACKUP_DIR/memories/USER.md"
  echo "  → USER.md salvo"
fi

# ── Config (sem secrets) ──────────────────────────────────────────────
echo "[3/5] Config..."
if [ -f "$HERMES_HOME/config.yaml" ]; then
  mkdir -p "$BACKUP_DIR/config"
  # Mascara tokens/keys/secrets
  sed 's/\(token\|key\|secret\|password\):.*/\1: ***MASKED***/gi' \
    "$HERMES_HOME/config.yaml" > "$BACKUP_DIR/config/config.yaml"
  echo "  → config.yaml salvo (secrets mascarados)"
fi

# ── Scripts personalizados ────────────────────────────────────────────
echo "[4/5] Scripts..."
mkdir -p "$BACKUP_DIR/scripts"
if ls "$HERMES_HOME/scripts/whatsapp"* >/dev/null 2>&1; then
  cp "$HERMES_HOME/scripts/whatsapp"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
if ls "$HERMES_HOME/scripts/qr-"* >/dev/null 2>&1; then
  cp "$HERMES_HOME/scripts/qr-"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
if ls "$HERMES_HOME/scripts/run-whatsapp"* >/dev/null 2>&1; then
  cp "$HERMES_HOME/scripts/run-whatsapp"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
if ls "$HERMES_HOME/scripts/setup-whatsapp"* >/dev/null 2>&1; then
  cp "$HERMES_HOME/scripts/setup-whatsapp"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
if ls "$HERMES_HOME/scripts/start-tunnel"* >/dev/null 2>&1; then
  cp "$HERMES_HOME/scripts/start-tunnel"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
if ls "$HERMES_HOME/scripts/tunnel-watchdog"* >/dev/null 2>&1; then
  cp "$HERMES_HOME/scripts/tunnel-watchdog"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
if ls "$HERMES_HOME/scripts/rocketstar"* >/dev/null 2>&1; then
  cp "$HERMES_HOME/scripts/rocketstar"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
fi
echo "  → $(find "$BACKUP_DIR/scripts" -type f 2>/dev/null | wc -l) scripts copiados"

# ── Session DB (opcional, pode ser grande) ────────────────────────────
# echo "[opcional] Session DB..."
# if [ -f "$HERMES_HOME/sessions.db" ]; then
#   mkdir -p "$BACKUP_DIR/sessions"
#   cp "$HERMES_HOME/sessions.db" "$BACKUP_DIR/sessions/"
# fi

echo ""
echo "=== Backup concluído ==="
echo ""
echo "Agora é só commitar e push:"
echo "  cd $HUB_DIR && git add -A && git commit -m \"backup: $(date +%Y-%m-%d)\" && git push"

Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
Taiff Connect: api.taiff-connect.com.br. Backend + PostgreSQL + RabbitMQ. Deploy GitHub Actions → EKS (Helm). Firebase: app-taiff. SendGrid: trial termina 03/ago/2026. Domínios: taiff-connect.com.br (DKIM verificado) vs taiff.com.br (não). gp2 StorageClass (WaitForFirstConsumer). Google Web Login: tokeninfo sem secret (client IDs: 458757385856-1o15s25 + 185745854158-fkc2f). Social: Google feito, Apple/Facebook pendentes. values-production.yaml + secret.yaml pra env vars. Padrão: branch → commit → push → PR → merge GitHub. Front mobile. DevOps gerencia cluster sem kubectl no PC do user. NUNCA mexer em rotas existentes sem análise de impacto.
§
AutoHedge bot: Dashboard 9120 + /tradeSol. Cron: análise 6h, MA Bounce 1h. extract_signal() híbrido (25/06). MAX_TRADE_USD=$1.00. Deposits $12.40. Resgate: key em Phantom. User quer aviso P&L positivo.
§
WhatsApp routing: bridge 3000 (principal, 5544991528386) = geral/ML/ecommerce. Bridge 3003 (NF-e, 554491277833) = SOMENTE NF-e. NUNCA cross-bridge. Envio: python3 /root/whatsapp-send/send-validated.py. Routing: /root/whatsapp-routing.json.
§
nfe-brasil: /opt/nfe-brasil. Docker compose: postgres:5433, redis:6380, evo:8085, mcp:8090, bot:3010. API key: nfe-brasil-2026. Whitelist: WHATSAPP_ALLOWED_USERS no compose. NUNCA sed dentro de container — sempre rebuild compose.
§
Taiff domínios: taiff-connect.com.br (SendGrid DKIM verificado), taiff.com.br (não verificado). Front usa client ID Firebase 185745854158-fkc2f... Pra email, melhor usar noreply@taiff-connect.com.br enquanto padronizam. SendGrid trial termina 03/ago/2026.
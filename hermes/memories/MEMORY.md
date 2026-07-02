Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
Taiff Connect: api.taiff-connect.com.br. Backend NestJS + PostgreSQL + RabbitMQ. Deploy GitHub Actions → EKS (Helm). SendGrid trial termina 03/ago/2026 — DOMÍNIO PROBLEMA: taiff.com.br tem DMARC p=reject, usar noreply@taiff-connect.com.br. Google Web Login: tokeninfo sem secret (458757385856-1o15s25 + 185745854158-fkc2f). Firebase só mobile. PVC uploads emptyDir (gp2 Pending). values-production.yaml SOBRESCREVE values.yaml. Front manda campos inglês, backend português (PR #104). Forgot-password: email+SMS, código 6 dígitos. Upload foto: campo "file". Test user: eng@ik1.com.br/eng@@2027. DevOps gerencia cluster. PRs: #93 Google multi-audience, #104 campos PT. NUNCA mexer em rotas sem análise.
§
AutoHedge: cron 6h + MA Bounce 1h. Dashboard 9120. Meta $5 lucro. Risk conservativo (user quer). MAX_TRADE_USD=1.00 (hardcodes $0.50 corrigidos). Credenciais: /root/mercadoLivre/dados.json.
§
WhatsApp routing: bridge 3000 (principal, 5544991528386) = geral/ML/ecommerce. Bridge 3003 (NF-e, 554491277833) = SOMENTE NF-e. NUNCA cross-bridge. Envio: python3 /root/whatsapp-send/send-validated.py. Routing: /root/whatsapp-routing.json.
§
nfe-brasil: /opt/nfe-brasil. Docker compose: postgres:5433, redis:6380, evo:8085, mcp:8090, bot:3010. API key: nfe-brasil-2026. Whitelist: WHATSAPP_ALLOWED_USERS no compose. NUNCA sed dentro de container — sempre rebuild compose.
§
CarCrew: PRs #53 (schema+sync ML, 12 produtos), #56 (frete checkout mock), #57 (galeria admin). Issues #54 (tela frete), #55 (integração frete standby). 36 produtos restantes sem preço. API ML dims em attributes[], token 6h.
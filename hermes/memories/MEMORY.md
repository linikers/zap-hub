Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
CarCrewCommerce (carcrew.com.br) — Next.js + Prisma + PostgreSQL (Vercel). `produtos.json` é fonte de dados mas site/admin lê do banco. Sincronizar: push main → Vercel build roda `prisma generate && npx prisma db seed && next build` com tsx. Cloudinary drvnlgib2/preset carcrew. Google Drive com pastas por produto (fotos + .txt). Fluxo: baixar drive → Cloudinary → update JSON → git push → deploy automático.
§
OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
Taiff Connect: api.taiff-connect.com.br. Deploy GitHub Actions (branch→PR→merge). Helm: helm/taiff-connect/. Firebase project: app-taiff. Social login: Firebase idToken expira 1h (fixo). JWT backend (30d) é separado. Fix app: getIdToken(true) pra refresh antes de /auth/social. FirebaseAuthProvider agora retorna erro real entre colchetes.
§
AutoHedge bot: Dashboard port 9120 + /tradeSol. Cron: análise 6h, MA Bounce 1h. Skill: autohedge-bot-management.
§
WhatsApp routing: bridge 3000 (principal, 5544991528386) = geral/ML/ecommerce. Bridge 3003 (NF-e, 554491277833) = SOMENTE NF-e. NUNCA cross-bridge. Envio: python3 /root/whatsapp-send/send-validated.py. Routing: /root/whatsapp-routing.json.
§
WhatsApp do Liniker: +55 44 991528386 (bridge 3000, geral/ML/ecommerce). NF-e bridge separada: 554491277833
§
Liniker quer bot WhatsApp 24h (sem horário comercial). Bot NF-e precisa de handlers pra intenções vagas ("emitir nota"), não só padrões exatos.
§
nfe-brasil: /opt/nfe-brasil — MCP server + WhatsApp bot + Evolution API v2.3.7. Docker compose: postgres:5433, redis:6380, evo:8085, mcp:8090, bot:3010. API key: nfe-brasil-2026. Fix: evo v2.3 manda data como LISTA no webhook (não dict). Whitelist: WHATSAPP_ALLOWED_USERS no compose (evita responder 62+ contatos). QR page: portfolio via /api/evo/ proxy. Portfolio repo: /root/portfolio/linikers. 24/7 (sem horário). NUNCA sed dentro de container — sempre rebuild compose.
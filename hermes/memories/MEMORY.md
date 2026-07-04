OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
Taiff Connect: NestJS+TypeORM+PostgreSQL. Deploy EKS (Helm+GitHub Actions). SendGrid email + Twilio SMS. Domínio: taiff.com.br (DMARC p=reject) → usa noreply@taiff-connect.com.br. PVC uploads: gp2 (Pending WaitForFirstConsumer). Profile: campos PT (PR #104/#106 cidade/estado). Google Web Login: tokeninfo (PR #91). Forgot-password: email+SMS código 6 dígitos. Upload foto: campo "file" (multer). Test: eng@ik1.com.br/eng@@2027. Issues: #107 Manuais/Notícias, #108 Biometria, #109 Foto URL. PRs: #58 OTA, #59 Add Device, #105/#106 profile. Git: liniker/linikers@hotmail.com.
§
AutoHedge: cron 6h + MA Bounce 1h. Dashboard 9120. Meta $5 lucro. MAX_TRADE_USD=1.00 ($0.50 corrigidos). Credenciais: /root/mercadoLivre/dados.json.
§
WhatsApp routing: bridge 3000 (principal, 5544991528386) = geral/ML/ecommerce. Bridge 3003 (NF-e, 554491277833) = SOMENTE NF-e. NUNCA cross-bridge. Envio: python3 /root/whatsapp-send/send-validated.py. Routing: /root/whatsapp-routing.json.
§
nfe-brasil: /opt/nfe-brasil. Docker: postgres:5433, redis:6380, evo:8085, mcp:8090, bot:3010. API key: nfe-brasil-2026. NUNCA sed dentro de container — sempre rebuild compose.
§
CarCrew Commerce: github.com/linikers/carCrewCommerce, Next.js 15+MUI v9+Prisma 7+PostgreSQL Neon (ep-dark-cell-acyfev6p-pooler.sa-east-1), Vercel. GA4 539721340, svc account carcrew@carcrew-501218.iam.gserviceaccount.com. Cloudinary drvnlgib2/carcrew. Business 5.0★ 121 reviews. SEO: 3 index/49 não-index. Keywords: oficina/rebaixados/suspensão ar/fixa/rosca/coilover/air lift Maringá. Vercel envs: GA4_SERVICE_ACCOUNT_EMAIL, GA4_SERVICE_ACCOUNT_KEY, GA4_PROPERTY_ID.
§
Vercel serverless: filesystem READ-ONLY. writeFileSync/readFileSync sempre falham. Persistência → banco (Prisma) ou API externa. Corrigimos pagamentos.json → Prisma Configuracao model + /api/pix.
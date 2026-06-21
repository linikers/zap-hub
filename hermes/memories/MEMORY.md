Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
CarCrewCommerce (carcrew.com.br) — Next.js + Prisma + PostgreSQL (Vercel). `produtos.json` é fonte de dados mas site/admin lê do banco. Sincronizar: push main → Vercel build roda `prisma generate && npx prisma db seed && next build` com tsx. Cloudinary drvnlgib2/preset carcrew. Google Drive com pastas por produto (fotos + .txt). Fluxo: baixar drive → Cloudinary → update JSON → git push → deploy automático.
§
Skill "pit-investimento" (business/) criada — PIT financeiro padronizado com custos por aluno, projeção 3 anos, valuation. Primeiro uso: gSimulados (10k alunos).
§
OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
Taiff backend: rotas novas = NUNCA quebrar existentes. Campos novos = opcional no Yup. Swagger completo /api-docs. Upload: multer + emptyDir (gp2 funciona, ebs-sc causa timeout). Forgot senha: SMS pronto (Twilio), email pendente.
§
Taiff: NUNCA quebrar rotas existentes do front. Campos novos = opcional no Yup. Sempre analisar impacto antes.
§
AutoHedge bot: Pipeline 4-agentes (Director→Quant→Risk→Execution). 23 fontes de dados reais: preços SOL/BTC/ETH, TVL (DefiLlama), Fear&Greed, RSI/MACD/Bollinger/EMA/ATR/SR/Fib, notícias RSS (CoinTelegraph+Decrypt). P&L vs preço depósito. Dashboard: port 9120 + /tradeSol. Trades bidirecionais. Cron: análise 6h, MA Bounce 1h. Skill: autohedge-bot-management.
§
WhatsApp routing: bridge 3000 (principal, 5544991528386) = geral/ML/ecommerce. Bridge 3003 (NF-e, 554491277833) = SOMENTE NF-e. NUNCA cross-bridge. Envio: python3 /root/whatsapp-send/send-validated.py. Routing: /root/whatsapp-routing.json.
§
PixelRAG instalado em /opt/pixelrag. Cmd: /opt/pixelrag/bin/pixelshot [URL] --output [DIR]. Renderiza web pages como screenshots tiles JPEG. Chrome headless em ~/.cache/pixelrag/chrome/. Útil pra ler gráficos de mercado como imagem.
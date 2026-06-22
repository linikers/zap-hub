Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
CarCrewCommerce (carcrew.com.br) — Next.js + Prisma + PostgreSQL (Vercel). `produtos.json` é fonte de dados mas site/admin lê do banco. Sincronizar: push main → Vercel build roda `prisma generate && npx prisma db seed && next build` com tsx. Cloudinary drvnlgib2/preset carcrew. Google Drive com pastas por produto (fotos + .txt). Fluxo: baixar drive → Cloudinary → update JSON → git push → deploy automático.
§
OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
Taiff backend: NUNCA quebrar rotas existentes. Campos novos = opcional no Yup. Swagger /api-docs. Upload multer. Forgot senha SMS pronto. Front diz que endpoints não retornam dados - precisa investigar.
§
AutoHedge bot: Pipeline 4-agentes (Director→Quant→Risk→Execution). 23 fontes de dados reais: preços SOL/BTC/ETH, TVL (DefiLlama), Fear&Greed, RSI/MACD/Bollinger/EMA/ATR/SR/Fib, notícias RSS (CoinTelegraph+Decrypt). P&L vs preço depósito. Dashboard: port 9120 + /tradeSol. Trades bidirecionais. Cron: análise 6h, MA Bounce 1h. Skill: autohedge-bot-management.
§
WhatsApp routing: bridge 3000 (principal, 5544991528386) = geral/ML/ecommerce. Bridge 3003 (NF-e, 554491277833) = SOMENTE NF-e. NUNCA cross-bridge. Envio: python3 /root/whatsapp-send/send-validated.py. Routing: /root/whatsapp-routing.json.
§
PixelRAG instalado em /opt/pixelrag. Cmd: /opt/pixelrag/bin/pixelshot [URL] --output [DIR]. Renderiza web pages como screenshots tiles JPEG. Chrome headless em ~/.cache/pixelrag/chrome/. Útil pra ler gráficos de mercado como imagem.
§
nfe-brasil: https://github.com/linikers/nfe-brasil — monorepo MCP server (49 tools NF-e/CT-e/MDF-e/NFC-e) + WhatsApp bot + Evolution API. Docker compose. Base: DeHor-Labs/mcp-fiscal-brasil (MIT). Evolution API: 8080, webhook → bot:3001 → MCP:8000.
§
WhatsApp do Liniker: +55 44 991528386 (bridge 3000, geral/ML/ecommerce). NF-e bridge separada: 554491277833
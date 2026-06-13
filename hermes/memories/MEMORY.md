erc20TokenLab (linikers/erc20TokenLab): curso Web3 R$19 em ecr20ttk.vercel.app. Pix estático OK.
§
Prefere posts de X/Twitter com tom leve, curioso e construtivo. NUNCA revoltado, negativo ou reclamão. "vc esta muito revoltado, paz no coração" — corrigiu explicitamente tom de desabafo. Posts devem soar como observação interessante, não reclamação.
§
autohedge-bot (linikers/autohedge-bot): CLI pipeline Director→Quant→Risk→Execution. Precisa OPENCODE_API_KEY. Pendente: frequencia execução + wallet.
§
zap-hub (linikers/zap-hub): repo de conexoes WhatsApp + backup do Hermes. drivers/ (cloud-api=simples, baileys=QR complexo), bots/ (nfe-baileys, ml-atendente-cloud), hermes/ (backup diario 8h com skills, memorias, crons, facts). Cron backup: 4df8558181f2.
§
Taiff Connect (SistemasTaiffProart/taiff-connect-backend): Node + Express 5 + TypeORM + PostgreSQL + RabbitMQ. RabbitMQ roda dentro do cluster EKS (rabbitmq.rabbitmq.svc.cluster.local). Deploy via Helm (chart em helm/taiff-connect) + GitHub Actions. Meu PAT não tem escopo workflow — não consigo alterar .github/workflows/ files; preparo o conteúdo e o usuário aplica manualmente.
§
Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
Taiff Connect RabbitMQ: migrado pra DNS interno rabbitmq.rabbitmq.svc.cluster.local. Readiness probe timeout corrigido (isConnected() nao tenta reconectar). Deploy EKS funcionando. Pipeline com debug step permanente. Frontend (dev): React 19 + Vite 7 + Tailwind 4, auth completo, dashboard vazio.
§
CarCrewCommerce (carcrew.com.br) — Next.js + Prisma + PostgreSQL (Vercel). `produtos.json` é fonte de dados mas site/admin lê do banco. Sincronizar: push main → Vercel build roda `prisma generate && npx prisma db seed && next build` com tsx. Cloudinary drvnlgib2/preset carcrew. Google Drive com pastas por produto (fotos + .txt). Fluxo: baixar drive → Cloudinary → update JSON → git push → deploy automático.
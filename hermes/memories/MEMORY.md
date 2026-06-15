erc20TokenLab (linikers/erc20TokenLab): curso Web3 R$19 em ecr20ttk.vercel.app. Pix estático OK.
§
Prefere posts de X/Twitter com tom leve, curioso e construtivo. NUNCA revoltado, negativo ou reclamão. "vc esta muito revoltado, paz no coração" — corrigiu explicitamente tom de desabafo. Posts devem soar como observação interessante, não reclamação.
§
autohedge-bot (linikers/autohedge-bot): CLI pipeline Director→Quant→Risk→Execution. Cron cada 6h desde 12/06. Pendente: configurar key Binance + API Key.
§
zap-hub (linikers/zap-hub): repo de conexoes WhatsApp + backup do Hermes. drivers/ (cloud-api=simples, baileys=QR complexo), bots/ (nfe-baileys, ml-atendente-cloud), hermes/ (backup diario 8h com skills, memorias, crons, facts). Cron backup: 4df8558181f2.
§
Taiff Connect: Node+Express5+TypeORM+PostgreSQL+RabbitMQ (DNS interno). EKS + Helm + GitHub Actions. PAT sem escopo workflow. Frontend: React19+Vite7+Tailwind4.
§
Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
CarCrewCommerce (carcrew.com.br) — Next.js + Prisma + PostgreSQL (Vercel). `produtos.json` é fonte de dados mas site/admin lê do banco. Sincronizar: push main → Vercel build roda `prisma generate && npx prisma db seed && next build` com tsx. Cloudinary drvnlgib2/preset carcrew. Google Drive com pastas por produto (fotos + .txt). Fluxo: baixar drive → Cloudinary → update JSON → git push → deploy automático.
§
Skill "pit-investimento" (business/) criada — PIT financeiro padronizado com custos por aluno, projeção 3 anos, valuation. Primeiro uso: gSimulados (10k alunos).
§
Taiff Connect backend (Express 5): req.params returns string | string[], not string. Destructuring const { id } = req.params infers string[] breaking tsc. Must always cast: const id = req.params.id as string. Pattern used across product-image, product-warranty, metadata, admin controllers.
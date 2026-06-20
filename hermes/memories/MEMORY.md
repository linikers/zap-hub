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
NUNCA modificar rotas existentes que o front possa consumir. Preferir rotas NOVAS. Se precisar mudar schema/resposta, tornar campos opcionais (Yup) pra não quebrar front. Sempre analisar impacto antes de implementar.
§
NF-e novo número: 44 9 9127-7833. Bridge separado na porta 3003 em modo bot com allowed users. Daemon NF-e rodando apontando pra porta 3003.
§
AutoHedge meta: $5 USD lucro. MA Bounce cíclica (compra+venda), $0.50/trade. Depósitos: 0.0374 SOL (2x). Dashboard lê index.json dinamicamente. X sem crédito.
§
Taiff branches: 1º firmware-update-ota (#58), 2º connect-device-flow (#59), 3º auth-registration. Upload: emptyDir padrão, PVC opcional com gp2 (ebs-sc causa timeout). Forgot senha: SMS pronto, email pendente. PRs #58/#59/#68 aguardam merge.